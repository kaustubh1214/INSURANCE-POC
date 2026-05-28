"""
Shared base mixin for all SQLAlchemy models.
Provides: UUID primary key, created_at, updated_at, is_active (soft delete).
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Adds created_at and updated_at to any model."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        server_default=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Adds is_active flag for soft deletes. Never hard-delete in production."""

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


class UUIDMixin:
    """Provides a UUID string primary key."""

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )


class BaseModelMixin(UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Full base mixin combining UUID PK + timestamps + soft delete.
    Use this on all domain models for consistency.
    """
    pass
