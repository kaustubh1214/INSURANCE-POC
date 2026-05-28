"""
Health Checkup and Lab Partner models.
Workflow: Employee books → assigned to lab → sample collected → reports uploaded.
"""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import BaseModelMixin


class LabPartner(BaseModelMixin, Base):
    """Partner diagnostic laboratory in the network."""

    __tablename__ = "lab_partners"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lat: Mapped[float | None] = mapped_column(nullable=True)
    lng: Mapped[float | None] = mapped_column(nullable=True)
    services: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON list of test types offered

    is_home_collection: Mapped[bool] = mapped_column(default=False)
    rating: Mapped[float | None] = mapped_column(nullable=True)

    checkups: Mapped[list["HealthCheckup"]] = relationship(
        "HealthCheckup", back_populates="lab_partner", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<LabPartner {self.name} city={self.city}>"


class HealthCheckup(BaseModelMixin, Base):
    """
    Scheduled health checkup booking.
    Full workflow: booked → sample_collected → reports_uploaded → completed.
    """

    __tablename__ = "health_checkups"

    employee_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("employees.id"), nullable=False, index=True
    )
    lab_partner_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("lab_partners.id"), nullable=True
    )

    # Booking details
    checkup_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # "annual_health_checkup" | "pre_policy" | "follow_up" | "diagnostics"

    package_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tests_requested: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON list of test names

    # Scheduling
    preferred_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    collection_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_home_collection: Mapped[bool] = mapped_column(default=False)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="booked")
    # "booked" | "confirmed" | "sample_collected" |
    # "reports_uploaded" | "completed" | "cancelled"

    # Results
    report_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    report_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_health_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    # AI-generated summary of health findings
    follow_up_recommended: Mapped[bool] = mapped_column(default=False)
    follow_up_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    employee: Mapped["Employee"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Employee", back_populates="health_checkups"
    )
    lab_partner: Mapped["LabPartner"] = relationship(
        "LabPartner", back_populates="checkups"
    )

    def __repr__(self) -> str:
        return f"<HealthCheckup type={self.checkup_type} status={self.status}>"
