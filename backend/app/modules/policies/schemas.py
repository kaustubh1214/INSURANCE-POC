"""Pydantic schemas for Policy and PolicyEnrollment endpoints."""
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field


class PolicyCreateRequest(BaseModel):
    policy_number: str = Field(min_length=3, max_length=100)
    policy_name: str = Field(min_length=3, max_length=255)
    policy_type: str
    insurer_name: str
    premium_amount: Decimal = Decimal("0")
    sum_insured: Decimal = Decimal("0")
    premium_frequency: str = "annual"
    policy_start_date: date | None = None
    policy_end_date: date | None = None
    description: str | None = None
    benefits_summary: str | None = None
    exclusions: str | None = None
    max_family_members: int = 4
    is_corporate: bool = True


class PolicyResponse(BaseModel):
    id: str
    policy_number: str
    policy_name: str
    policy_type: str
    insurer_name: str
    premium_amount: Decimal
    sum_insured: Decimal
    premium_frequency: str
    policy_start_date: date | None
    policy_end_date: date | None
    description: str | None
    benefits_summary: str | None
    max_family_members: int
    is_corporate: bool
    is_active: bool

    model_config = {"from_attributes": True}


class EnrollmentCreateRequest(BaseModel):
    policy_id: str
    enrollment_date: date
    coverage_start_date: date | None = None
    coverage_end_date: date | None = None


class EnrollmentResponse(BaseModel):
    id: str
    employee_id: str
    policy_id: str
    enrollment_date: date
    coverage_start_date: date | None
    coverage_end_date: date | None
    enrollment_status: str
    sum_insured: Decimal | None
    certificate_number: str | None

    model_config = {"from_attributes": True}
