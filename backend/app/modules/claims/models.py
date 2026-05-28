"""
Claims models.
- Claim: Main claim record with state machine
- ClaimDocument: Documents attached to a claim
- ClaimStatusHistory: Immutable audit trail of status transitions
"""
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import BaseModelMixin, UUIDMixin


# ---------------------------------------------------------------------------
# Claim Status Constants
# ---------------------------------------------------------------------------
class ClaimStatus:
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_DOCS = "pending_documents"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SETTLED = "settled"
    WITHDRAWN = "withdrawn"

    ALL = [
        DRAFT, SUBMITTED, PENDING_DOCS,
        UNDER_REVIEW, APPROVED, REJECTED, SETTLED, WITHDRAWN
    ]

    # Valid transitions: {current_status: [allowed_next_statuses]}
    TRANSITIONS = {
        DRAFT: [SUBMITTED, WITHDRAWN],
        SUBMITTED: [PENDING_DOCS, UNDER_REVIEW, WITHDRAWN],
        PENDING_DOCS: [SUBMITTED, WITHDRAWN],
        UNDER_REVIEW: [APPROVED, REJECTED, PENDING_DOCS],
        APPROVED: [SETTLED],
        REJECTED: [],          # Terminal state
        SETTLED: [],           # Terminal state
        WITHDRAWN: [],         # Terminal state
    }


class Claim(BaseModelMixin, Base):
    """
    Insurance claim — central entity in the claims workflow.
    Status follows a strict state machine (see ClaimStatus.TRANSITIONS).
    """

    __tablename__ = "claims"

    # Claim identity
    claim_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )

    # References
    employee_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("employees.id"), nullable=False, index=True
    )
    enrollment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("policy_enrollments.id"), nullable=False, index=True
    )

    # Patient (could be employee or family member)
    patient_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="employee"
    )
    # "employee" | "family_member"
    family_member_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("family_members.id"), nullable=True
    )

    # Claim details
    claim_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # "hospitalization" | "outpatient" | "dental" | "vision" | "pharmacy" | "accident"

    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    hospital_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    treatment_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    treatment_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Financial
    claimed_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=0
    )
    approved_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    settled_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    deductible_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    # Status (state machine)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=ClaimStatus.DRAFT, index=True
    )

    # AI analysis results
    ai_fraud_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    # 0.0 = low risk, 1.0 = high fraud risk
    ai_priority_score: Mapped[float | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    ai_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_missing_docs: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON list of missing document names

    # Processing
    assigned_to: Mapped[str | None] = mapped_column(String(36), nullable=True)
    # User ID of the insurer/admin handling this claim
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    settlement_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    settlement_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Submission metadata
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Employee", back_populates="claims"
    )
    enrollment: Mapped["PolicyEnrollment"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "PolicyEnrollment", back_populates="claims"
    )
    documents: Mapped[list["ClaimDocument"]] = relationship(
        "ClaimDocument", back_populates="claim", lazy="select"
    )
    status_history: Mapped[list["ClaimStatusHistory"]] = relationship(
        "ClaimStatusHistory",
        back_populates="claim",
        order_by="ClaimStatusHistory.changed_at",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Claim {self.claim_number} status={self.status}>"


class ClaimDocument(BaseModelMixin, Base):
    """
    Documents uploaded as part of a claim.
    Stores file metadata + OCR extraction results.
    """

    __tablename__ = "claim_documents"

    claim_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("claims.id"), nullable=False, index=True
    )

    # File info
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # "discharge_summary" | "bills" | "prescription" | "lab_report" |
    # "aadhaar" | "pan" | "insurance_card" | "other"
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_kb: Mapped[int | None] = mapped_column(nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # OCR results
    ocr_status: Mapped[str] = mapped_column(String(50), default="pending")
    # "pending" | "processing" | "completed" | "failed"
    ocr_extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_structured_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON string of extracted structured fields

    # Validation
    is_verified: Mapped[bool] = mapped_column(default=False)
    verification_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Uploaded by
    uploaded_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Relationship
    claim: Mapped["Claim"] = relationship("Claim", back_populates="documents")

    def __repr__(self) -> str:
        return f"<ClaimDocument type={self.document_type} claim={self.claim_id}>"


class ClaimStatusHistory(UUIDMixin, Base):
    """
    Immutable audit trail of every claim status change.
    Written on every status transition — never updated or deleted.
    """

    __tablename__ = "claim_status_history"

    claim_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("claims.id"), nullable=False, index=True
    )

    # Transition data
    from_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(),
        server_default=func.now(),
    )
    changed_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    changed_by_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    change_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # System vs manual
    is_system_action: Mapped[bool] = mapped_column(default=False)
    # True if triggered by AI/automation

    # Relationship
    claim: Mapped["Claim"] = relationship("Claim", back_populates="status_history")

    def __repr__(self) -> str:
        return (
            f"<ClaimStatusHistory {self.from_status}→{self.to_status} "
            f"claim={self.claim_id}>"
        )
