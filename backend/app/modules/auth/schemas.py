"""Pydantic schemas for authentication endpoints."""
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Request body for user registration."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    role: str = Field(default="employee")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        allowed = ["admin", "hr", "employee", "insurer", "agent"]
        if v not in allowed:
            raise ValueError(f"Role must be one of: {allowed}")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    """Request body for login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token pair returned on login/refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires


class RefreshRequest(BaseModel):
    """Request body for token refresh."""

    refresh_token: str


class CurrentUserResponse(BaseModel):
    """Minimal user info embedded in token / returned by /me."""

    id: str
    email: str
    full_name: str
    role: str
    is_verified: bool

    model_config = {"from_attributes": True}
