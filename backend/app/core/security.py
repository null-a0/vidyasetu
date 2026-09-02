from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Return bcrypt hash of *plain* text password."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*."""
    return _pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------


def _create_token(
    subject: str,
    role: str,
    token_type: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Encode a signed JWT with ``sub`` and ``role`` claims.

    Args:
        subject: The user's primary key (UUID string).
        role: The user's role string (e.g. ``"student"``).
        expires_delta: Token lifetime. Caller controls default per token type.
    """
    expire = datetime.now(tz=timezone.utc) + expires_delta
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "typ": token_type,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(
    subject: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a short-lived access token."""
    return _create_token(
        subject=subject,
        role=role,
        token_type="access",
        expires_delta=expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(
    subject: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a long-lived refresh token."""
    return _create_token(
        subject=subject,
        role=role,
        token_type="refresh",
        expires_delta=expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT.

    Returns the raw payload dict on success.

    Raises:
        jose.JWTError: If the token is invalid or expired.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    token_type = payload.get("typ")
    if token_type and token_type != "access":
        raise JWTError("Invalid token type for access token")
    return payload


def decode_refresh_token(token: str) -> dict[str, Any]:
    """Decode and verify a refresh JWT."""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if payload.get("typ") != "refresh":
        raise JWTError("Invalid token type for refresh token")
    return payload


# ---------------------------------------------------------------------------
# Password reset tokens
# ---------------------------------------------------------------------------


def _password_fingerprint(password_hash: str) -> str:
    return hashlib.sha256(password_hash.encode("utf-8")).hexdigest()[:16]


def create_password_reset_token(subject: str, password_hash: str) -> str:
    """Create a single-use reset token bound to the user's current password hash.

    Because the token embeds a fingerprint of the current hash, it becomes
    invalid as soon as the password changes, so it cannot be replayed.
    """
    expire = datetime.now(tz=timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "typ": "reset",
        "pwd": _password_fingerprint(password_hash),
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_password_reset_token(token: str, password_hash: str) -> dict[str, Any]:
    """Decode a reset token and verify it matches the user's current password hash.

    Raises:
        jose.JWTError: If the token is invalid, expired, or already used.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if payload.get("typ") != "reset":
        raise JWTError("Invalid token type for password reset token")
    if payload.get("pwd") != _password_fingerprint(password_hash):
        raise JWTError("Password reset token is no longer valid")
    return payload
