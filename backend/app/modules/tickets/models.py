"""
Ticket model — customer support requests.
AI-powered categorization and resolution suggestions.
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import BaseModelMixin


class Ticket(BaseModelMixin, Base):
    """
    Support ticket raised by an employee or agent.
    AI assists with categorization and suggested resolutions.
    """

    __tablename__ = "tickets"

    # Ticket identity
    ticket_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    # Submitter
    created_by_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )

    # Content
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Classification
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # "claim_query" | "policy_query" | "payment" | "card_issue" |
    # "enrollment" | "technical" | "general"
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    # "low" | "medium" | "high" | "critical"

    # Status
    status: Mapped[str] = mapped_column(String(50), default="open")
    # "open" | "in_progress" | "waiting_on_user" | "resolved" | "closed"

    # Assignment
    assigned_to_user_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True
    )

    # AI assistance
    ai_category_suggestion: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ai_resolution_suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_auto_resolved: Mapped[bool] = mapped_column(default=False)
    # True if AI resolved without human intervention

    # Related resource
    related_claim_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    related_policy_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Timestamps
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Satisfaction
    satisfaction_rating: Mapped[int | None] = mapped_column(nullable=True)
    # 1-5

    # Relationship
    created_by_user: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", back_populates="tickets"
    )

    def __repr__(self) -> str:
        return f"<Ticket {self.ticket_number} status={self.status}>"
