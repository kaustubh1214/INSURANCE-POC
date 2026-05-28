"""
Family Member model — dependents of an employee covered under insurance.
"""
from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship as sa_relationship

from app.database import Base
from app.models.base import BaseModelMixin


class FamilyMember(BaseModelMixin, Base):
    """
    Dependent family members of an employee.
    Covered under the employee's policy enrollment.
    """

    __tablename__ = "family_members"

    # Link to employee
    employee_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("employees.id"), nullable=False, index=True
    )

    # Personal info (PII — masked before AI calls)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship: Mapped[str] = mapped_column(String(50), nullable=False)
    # "spouse" | "child" | "parent" | "sibling"
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Identity docs (PII)
    aadhaar_number: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Coverage
    is_covered_under_policy: Mapped[bool] = mapped_column(default=True)

    # Relationships
    employee: Mapped["Employee"] = sa_relationship(  # type: ignore[name-defined]  # noqa: F821
        "Employee", back_populates="family_members"
    )

    def __repr__(self) -> str:
        return f"<FamilyMember name={self.full_name} relation={self.relationship}>"
