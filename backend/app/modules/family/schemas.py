"""Pydantic schemas for Family Member endpoints."""
from datetime import date
from pydantic import BaseModel, Field


class FamilyMemberCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    relationship: str = Field(description="spouse|child|parent|sibling")
    date_of_birth: date | None = None
    gender: str | None = None
    aadhaar_number: str | None = None
    is_covered_under_policy: bool = True


class FamilyMemberUpdateRequest(BaseModel):
    full_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    aadhaar_number: str | None = None
    is_covered_under_policy: bool | None = None


class FamilyMemberResponse(BaseModel):
    id: str
    employee_id: str
    full_name: str
    relationship: str
    date_of_birth: date | None
    gender: str | None
    is_covered_under_policy: bool
    is_active: bool

    model_config = {"from_attributes": True}
