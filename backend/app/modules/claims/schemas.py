"""Pydantic schemas for Claims endpoints."""
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class ClaimCreateRequest(BaseModel):
    enrollment_id: str
    claim_type: str = Field(description="hospitalization|outpatient|dental|vision|pharmacy|accident")
    diagnosis: str | None = None
    hospital_name: str | None = None
    treatment_start_date: date | None = None
    treatment_end_date: date | None = None
    claimed_amount: Decimal = Decimal("0")
    patient_type: str = "employee"
    family_member_id: str | None = None
    notes: str | None = None


class ClaimStatusUpdateRequest(BaseModel):
    status: str
    change_reason: str | None = None
    notes: str | None = None
    approved_amount: Decimal | None = None
    rejection_reason: str | None = None


class ClaimResponse(BaseModel):
    id: str
    claim_number: str
    employee_id: str
    enrollment_id: str
    claim_type: str
    status: str
    claimed_amount: Decimal
    approved_amount: Decimal | None
    settled_amount: Decimal | None
    diagnosis: str | None
    hospital_name: str | None
    treatment_start_date: date | None
    treatment_end_date: date | None
    patient_type: str
    ai_fraud_score: float | None
    ai_priority_score: float | None
    ai_category: str | None
    ai_summary: str | None
    ai_missing_docs: str | None
    submitted_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClaimDocumentResponse(BaseModel):
    id: str
    claim_id: str
    document_type: str
    file_name: str
    ocr_status: str
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ClaimStatusHistoryResponse(BaseModel):
    id: str
    from_status: str | None
    to_status: str
    changed_at: datetime
    changed_by_name: str | None
    change_reason: str | None
    is_system_action: bool

    model_config = {"from_attributes": True}
