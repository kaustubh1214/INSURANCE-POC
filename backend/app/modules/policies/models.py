"""
Policy and PolicyEnrollment models.
Policies: insurance product definitions.
PolicyEnrollment: maps employee → policy (many-to-many with metadata).
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import BaseModelMixin


class Policy(BaseModelMixin, Base):
    """
    Insurance policy product definition.
    Created by admin/insurer.
    Employees enroll in policies.
    """

    __tablename__ = "policies"

    # Identity
    policy_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    policy_name: Mapped[str] = mapped_column(String(255), nullable=False)
    policy_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # "health" | "life" | "accidental" | "dental" | "vision" | "term"

    # Insurer
    insurer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    insurer_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Financial
    premium_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=0
    )
    sum_insured: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=0
    )
    premium_frequency: Mapped[str] = mapped_column(
        String(50), default="annual"
    )
    # "monthly" | "quarterly" | "annual"

    # Coverage period
    policy_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    policy_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Details
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    benefits_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    exclusions: Mapped[str | None] = mapped_column(Text, nullable=True)
    terms_and_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Metadata
    max_family_members: Mapped[int] = mapped_column(default=4)
    is_corporate: Mapped[bool] = mapped_column(default=True)
    # corporate = employer-sponsored | personal = individual

    # Relationships
    enrollments: Mapped[list["PolicyEnrollment"]] = relationship(
        "PolicyEnrollment", back_populates="policy", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Policy {self.policy_number} type={self.policy_type}>"


class PolicyEnrollment(BaseModelMixin, Base):
    """
    Employee enrollment in a policy.
    Tracks the specific coverage for this employee under this policy.
    """

    __tablename__ = "policy_enrollments"

    # References
    employee_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("employees.id"), nullable=False, index=True
    )
    policy_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("policies.id"), nullable=False, index=True
    )

    # Enrollment-specific data
    enrollment_date: Mapped[date] = mapped_column(Date, nullable=False)
    coverage_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    coverage_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Status
    enrollment_status: Mapped[str] = mapped_column(String(50), default="active")
    # "active" | "expired" | "cancelled" | "pending"

    # Coverage amount (may differ per employee based on grade)
    sum_insured: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    employee_premium: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    employer_premium: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    # Card / certificate number
    certificate_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Employee", back_populates="policy_enrollments"
    )
    policy: Mapped["Policy"] = relationship(
        "Policy", back_populates="enrollments"
    )
    claims: Mapped[list["Claim"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Claim", back_populates="enrollment", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<PolicyEnrollment emp={self.employee_id} policy={self.policy_id}>"
