"""
Audit log writer.
Call write_audit_log() after every state-changing operation.
"""
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog, AIAuditLog


async def write_audit_log(
    db: AsyncSession,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    user_id: str | None = None,
    user_email: str | None = None,
    user_role: str | None = None,
    old_value: Any = None,
    new_value: Any = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    request_id: str | None = None,
    notes: str | None = None,
    status: str = "success",
) -> None:
    """
    Write an immutable audit log entry.

    Args:
        action: What happened, e.g. "CREATE_CLAIM", "UPDATE_STATUS"
        resource_type: What was acted on, e.g. "claim", "user"
        resource_id: UUID of the resource
        user_id: Who did it
        old_value: State before change (will be JSON-serialized)
        new_value: State after change (will be JSON-serialized)
    """
    log = AuditLog(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        user_email=user_email,
        user_role=user_role,
        old_value=json.dumps(old_value, default=str) if old_value else None,
        new_value=json.dumps(new_value, default=str) if new_value else None,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
        notes=notes,
        status=status,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(log)
    # Note: do NOT call db.commit() here — let the request's session handle it.
    # This ensures audit logs are rolled back if the main operation fails.


async def write_ai_audit_log(
    db: AsyncSession,
    service_name: str,
    model_name: str,
    masked_input: str | None = None,
    response_summary: str | None = None,
    user_id: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    latency_ms: float | None = None,
    status: str = "success",
    error_message: str | None = None,
    prompt_hash: str | None = None,
) -> None:
    """
    Write an AI interaction audit log.
    IMPORTANT: masked_input must have PII removed before calling this.
    """
    log = AIAuditLog(
        service_name=service_name,
        model_name=model_name,
        masked_input=masked_input,
        response_summary=response_summary,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        status=status,
        error_message=error_message,
        prompt_hash=prompt_hash,
    )
    db.add(log)
