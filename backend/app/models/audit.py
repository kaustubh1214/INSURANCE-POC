"""
Audit log models.
- AuditLog: Tracks every state-changing operation in the system.
- AIAuditLog: Tracks every AI/LLM interaction (compliance requirement).
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AuditLog(Base):
    """
    Immutable audit trail for all system mutations.
    Written on every CREATE, UPDATE, DELETE operation.
    """

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, server_default=func.now()
    )

    # Who performed the action
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    user_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_role: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # What they did
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g. "CREATE_CLAIM", "UPDATE_CLAIM_STATUS", "DELETE_USER"

    # Which resource
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g. "claim", "policy", "user"
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Request context
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Change data (before/after state)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Additional context
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="success")
    # "success" | "failure"


class AIAuditLog(Base):
    """
    Compliance audit log for every AI/LLM interaction.
    Required by enterprise security policy.
    Stores MASKED inputs — never raw PII.
    """

    __tablename__ = "ai_audit_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, server_default=func.now()
    )

    # Who triggered the AI call
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    session_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # What AI service was used
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g. "claim_classifier", "rag_chatbot", "ocr_extractor"
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g. "gpt-4o", "claude-3-sonnet"

    # Request/Response (MASKED — no raw PII)
    prompt_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # SHA-256 hash of masked prompt (for dedup, not reversible)
    masked_input: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Token usage (for cost tracking)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Performance
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Outcome
    status: Mapped[str] = mapped_column(String(20), default="success")
    # "success" | "failure" | "hallucination_flagged" | "pii_detected"
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Related resource
    resource_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
