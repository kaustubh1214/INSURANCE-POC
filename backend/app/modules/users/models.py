"""
User model — authentication account for any system user.
Roles: admin, hr, employee, insurer, agent
"""
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import BaseModelMixin


class User(BaseModelMixin, Base):
    """
    Core authentication entity.
    One user account maps to one role.
    Employees have a linked Employee record.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Role-based access control
    # Roles: admin | hr | employee | insurer | agent
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="employee")

    # Account state
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # Refresh token (stored for invalidation)
    refresh_token: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Employee",
        back_populates="user",
        uselist=False,
        lazy="selectin",
    )
    tickets: Mapped[list["Ticket"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Ticket", back_populates="created_by_user", lazy="select"
    )
    notifications: Mapped[list["Notification"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Notification", back_populates="user", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
