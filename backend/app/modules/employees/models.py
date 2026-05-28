"""
Employee model — profile linked to a User account.
Stores employment-specific information.
"""
from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import BaseModelMixin


class Employee(BaseModelMixin, Base):
    """
    Employee profile.
    Linked 1:1 to a User (the auth account).
    Contains HR and employment data.
    """

    __tablename__ = "employees"

    # Link to auth account
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), unique=True, nullable=False, index=True
    )

    # Employment details
    employee_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    designation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date_of_joining: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_of_leaving: Mapped[date | None] = mapped_column(Date, nullable=True)
    employment_status: Mapped[str] = mapped_column(
        String(50), default="active"
    )
    # "active" | "on_leave" | "resigned" | "terminated"

    # Personal details (PII — masked before AI calls)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    aadhaar_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pan_number: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Address
    address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Company / HR hierarchy
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manager_employee_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("employees.id"), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", back_populates="employee"
    )
    family_members: Mapped[list["FamilyMember"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "FamilyMember", back_populates="employee", lazy="select"
    )
    policy_enrollments: Mapped[list["PolicyEnrollment"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "PolicyEnrollment", back_populates="employee", lazy="select"
    )
    claims: Mapped[list["Claim"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Claim", back_populates="employee", lazy="select"
    )
    health_card: Mapped["HealthCard"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "HealthCard", back_populates="employee", uselist=False, lazy="selectin"
    )
    health_checkups: Mapped[list["HealthCheckup"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "HealthCheckup", back_populates="employee", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Employee code={self.employee_code} dept={self.department}>"
