"""
Notification model — in-app and push notifications for users.
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import BaseModelMixin


class Notification(BaseModelMixin, Base):
    """
    In-app notification for a user.
    Also serves as the record for email/SMS dispatched notifications.
    """

    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )

    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Type
    notification_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # "claim_update" | "policy_renewal" | "checkup_reminder" |
    # "ticket_update" | "document_required" | "general"

    # Channel
    channel: Mapped[str] = mapped_column(String(50), default="in_app")
    # "in_app" | "email" | "sms" | "push"

    # Status
    is_read: Mapped[bool] = mapped_column(default=False)
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Related resource
    action_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resource_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Delivery tracking
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivery_status: Mapped[str] = mapped_column(String(50), default="pending")
    # "pending" | "sent" | "delivered" | "failed"

    # Relationship
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", back_populates="notifications"
    )

    def __repr__(self) -> str:
        return f"<Notification type={self.notification_type} user={self.user_id}>"
