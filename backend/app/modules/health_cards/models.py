"""
Health Card model — digital/physical insurance health card per employee.
"""
from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import BaseModelMixin


class HealthCard(BaseModelMixin, Base):
    """
    Insurance health card issued to an employee.
    Generated from policy enrollment.
    """

    __tablename__ = "health_cards"

    # Link
    employee_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("employees.id"), unique=True, nullable=False, index=True
    )
    enrollment_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("policy_enrollments.id"), nullable=True
    )

    # Card details
    card_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    insurer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    plan_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    network_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # "cashless" | "reimbursement" | "both"

    # Validity
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date] = mapped_column(Date, nullable=False)

    # Coverage
    sum_insured: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Stored as string to support "5,00,000" format for display

    # TPA (Third Party Administrator)
    tpa_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tpa_helpline: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tpa_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Emergency contacts
    emergency_contact: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Status
    card_status: Mapped[str] = mapped_column(String(50), default="active")
    # "active" | "expired" | "suspended" | "cancelled"

    # QR/barcode
    qr_code_data: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationship
    employee: Mapped["Employee"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Employee", back_populates="health_card"
    )

    def __repr__(self) -> str:
        return f"<HealthCard {self.card_number} status={self.card_status}>"
