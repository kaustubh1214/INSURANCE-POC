"""Pydantic schemas for Employee endpoints."""
from datetime import date
from pydantic import BaseModel, Field


class EmployeeCreateRequest(BaseModel):
    user_id: str
    employee_code: str = Field(min_length=2, max_length=50)
    department: str | None = None
    designation: str | None = None
    date_of_joining: date | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    aadhaar_number: str | None = None
    pan_number: str | None = None
    address_line1: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    company_name: str | None = None


class EmployeeUpdateRequest(BaseModel):
    department: str | None = None
    designation: str | None = None
    date_of_birth: date | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    employment_status: str | None = None


class EmployeeResponse(BaseModel):
    id: str
    user_id: str
    employee_code: str
    department: str | None
    designation: str | None
    date_of_joining: date | None
    employment_status: str
    company_name: str | None
    city: str | None
    state: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class EmployeeDetailResponse(EmployeeResponse):
    """Full employee profile including PII fields."""
    date_of_birth: date | None
    gender: str | None
    aadhaar_number: str | None
    pan_number: str | None
    address_line1: str | None
    address_line2: str | None
    pincode: str | None
