"""Pydantic schemas for User CRUD endpoints."""
from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: str | None
    role: str
    is_verified: bool
    is_active: bool

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=20)


class UserRoleUpdateRequest(BaseModel):
    role: str

    @classmethod
    def validate_role(cls, v: str) -> str:
        allowed = ["admin", "hr", "employee", "insurer", "agent"]
        if v not in allowed:
            raise ValueError(f"Role must be one of: {allowed}")
        return v
