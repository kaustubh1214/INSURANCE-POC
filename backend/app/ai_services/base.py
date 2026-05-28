"""
Base AI Service class.
All AI service classes inherit from this.
Provides: PII masking, audit logging, error handling, latency tracking.
"""
import time
from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_services.pii_masker import hash_prompt, mask_pii
from app.core.audit import write_ai_audit_log


class BaseAIService(ABC):
    """
    Base class for all AI/LLM services.

    Subclasses must implement: `_call_model()`
    Call `run()` from outside — it handles masking, logging, timing.
    """

    SERVICE_NAME: str = "base_ai_service"
    MODEL_NAME: str = "unknown"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def run(
        self,
        input_text: str,
        user_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Execute the AI service with full audit trail.

        Steps:
        1. Mask PII from input
        2. Call the model
        3. Log to ai_audit_logs
        4. Return result

        Returns:
            {
                "result": <model output>,
                "latency_ms": float,
                "status": "success" | "failure",
                "error": str | None
            }
        """
        masked_input = mask_pii(input_text)
        prompt_hash = hash_prompt(masked_input)

        start_time = time.monotonic()
        result = None
        status = "success"
        error_message = None
        input_tokens = None
        output_tokens = None

        try:
            result, input_tokens, output_tokens = await self._call_model(
                masked_input, **kwargs
            )
        except Exception as exc:
            status = "failure"
            error_message = str(exc)
            result = None

        latency_ms = (time.monotonic() - start_time) * 1000

        # Always log AI interactions
        await write_ai_audit_log(
            db=self.db,
            service_name=self.SERVICE_NAME,
            model_name=self.MODEL_NAME,
            masked_input=masked_input[:2000],  # Truncate for storage
            response_summary=str(result)[:500] if result else None,
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

        return {
            "result": result,
            "latency_ms": round(latency_ms, 2),
            "status": status,
            "error": error_message,
        }

    @abstractmethod
    async def _call_model(
        self, masked_input: str, **kwargs
    ) -> tuple[Any, int | None, int | None]:
        """
        Implement this in each subclass.
        Returns: (result, input_tokens, output_tokens)
        """
        ...
