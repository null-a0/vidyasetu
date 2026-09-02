from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.config import settings
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_password_reset_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.crud import create_user, get_user_by_email
from app.models import User, UserRole
from app.schemas.user import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserResponse,
)
from app.services.email import send_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student account",
)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Public self-registration. Always creates a ``student``; staff accounts
    must be provisioned by an admin via ``POST /auth/users``."""
    existing = await get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with that email already exists.",
        )
    user = await create_user(db, payload.to_user_create())
    return UserResponse.model_validate(user)


# ---------------------------------------------------------------------------
# POST /auth/users  (staff provisioning)
# ---------------------------------------------------------------------------


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user with an explicit role (admin / institution admin only)",
)
async def create_user_with_role(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> UserResponse:
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if payload.role not in (UserRole.STUDENT, UserRole.EDUCATOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Institution admins can only create students and educators.",
            )
        if not current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Institution admin is not linked to any institution.",
            )
        payload.institution_id = current_user.institution_id

    existing = await get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with that email already exists.",
        )
    user = await create_user(db, payload)
    return UserResponse.model_validate(user)


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------


@router.post("/login", response_model=Token, summary="Obtain a JWT access token")
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    user = await get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Check that the selected role matches the user's actual role
    if payload.role != user.role.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role mismatch. You must select your assigned role: {user.role.value}",
        )
    access_token = create_access_token(subject=user.id, role=user.role.value)
    refresh_token = create_refresh_token(subject=user.id, role=user.role.value)
    return Token(access_token=access_token, refresh_token=refresh_token)


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------


@router.post("/refresh", response_model=Token, summary="Refresh an access token")
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Issue fresh access + refresh tokens from a valid refresh token."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_payload = decode_refresh_token(payload.refresh_token)
        user_id = str(token_payload.get("sub") or "")
        if not user_id:
            raise credentials_exc
    except Exception:
        raise credentials_exc

    user = await db.get(User, user_id)
    if not user:
        raise credentials_exc

    access_token = create_access_token(subject=user.id, role=user.role.value)
    refresh_token = create_refresh_token(subject=user.id, role=user.role.value)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Start password reset flow",
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    # Always return the same generic message so the endpoint cannot be used
    # to enumerate accounts.
    user = await get_user_by_email(db, payload.email)
    if user:
        token = create_password_reset_token(subject=user.id, password_hash=user.password)
        frontend_origin = settings.frontend_origins[0] if settings.frontend_origins else settings.BASE_URL
        reset_link = f"{frontend_origin.rstrip('/')}/reset-password#token={token}"
        if settings.DEBUG and not settings.SMTP_HOST:
            logger.warning("SMTP not configured; password reset link for %s: %s", user.email, reset_link)
        background_tasks.add_task(
            _send_reset_email,
            to_email=user.email,
            reset_link=reset_link,
        )
    return MessageResponse(message="If an account exists for that email, password reset instructions have been initiated.")


def _send_reset_email(*, to_email: str, reset_link: str) -> None:
    try:
        send_email(
            to_email=to_email,
            subject=f"{settings.APP_NAME} password reset",
            body=(
                "We received a request to reset your password.\n\n"
                f"Use this link within {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes:\n{reset_link}\n\n"
                "If you did not request this, you can ignore this email."
            ),
        )
    except Exception:
        logger.exception("Failed to send password reset email")


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password using a reset token from the forgot-password email",
)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    invalid_exc = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired password reset token.",
    )
    try:
        unverified = jwt.get_unverified_claims(payload.token)
        user_id = str(unverified.get("sub") or "")
    except JWTError:
        raise invalid_exc
    if not user_id:
        raise invalid_exc

    user = await db.get(User, user_id)
    if not user:
        raise invalid_exc

    try:
        decode_password_reset_token(payload.token, password_hash=user.password)
    except JWTError:
        raise invalid_exc

    user.password = hash_password(payload.new_password)
    await db.flush()
    await db.commit()
    return MessageResponse(message="Password updated successfully.")
