from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, field_validator, model_validator

from app.models import UserRole


# ---------------------------------------------------------------------------
# Sub-schemas
# ---------------------------------------------------------------------------


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # user id
    role: UserRole


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.STUDENT
    institution_id: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    department: Optional[str] = None
    parent_name: Optional[str] = None
    parent_email: Optional[EmailStr] = None
    institution_admin_name: Optional[str] = None
    institution_admin_address: Optional[str] = None
    institution_admin_code: Optional[str] = None


class RegisterRequest(BaseModel):
    """Public self-registration payload. Role is always student; institution_id is never accepted."""

    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    bio: Optional[str] = None
    parent_name: Optional[str] = None
    parent_email: Optional[EmailStr] = None

    def to_user_create(self) -> "UserCreate":
        return UserCreate(
            name=self.name,
            email=self.email,
            password=self.password,
            role=UserRole.STUDENT,
            phone=self.phone,
            bio=self.bio,
            parent_name=self.parent_name,
            parent_email=self.parent_email,
        )


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    profile_photo: Optional[str] = None
    bio: Optional[str] = None
    department: Optional[str] = None
    parent_name: Optional[str] = None
    parent_email: Optional[EmailStr] = None
    institution_admin_name: Optional[str] = None
    institution_admin_address: Optional[str] = None
    institution_admin_code: Optional[str] = None
    theme: Optional[Literal["light", "dark"]] = None
    institution_id: Optional[str] = None


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: Optional[str]
    email: str
    role: UserRole
    institution_id: Optional[str]
    phone: Optional[str]
    profile_photo: Optional[str]
    bio: Optional[str]
    department: Optional[str]
    parent_name: Optional[str]
    parent_email: Optional[EmailStr]
    institution_admin_name: Optional[str]
    institution_admin_address: Optional[str]
    institution_admin_code: Optional[str]
    theme: Optional[str]
    salary_amount: Optional[int] = 0
    salary_type: Optional[str] = "monthly"
    created_at: Optional[datetime]


# ---------------------------------------------------------------------------
# Institution
# ---------------------------------------------------------------------------


class InstitutionCreate(BaseModel):
    name: str
    address: Optional[str] = None
    admin_id: Optional[str] = None


class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    admin_id: Optional[str] = None


class InstitutionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    address: Optional[str]
    admin_id: Optional[str]


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str  # Added: role selected by user


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class MessageResponse(BaseModel):
    message: str
