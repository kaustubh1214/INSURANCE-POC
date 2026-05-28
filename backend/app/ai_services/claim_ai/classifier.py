"""
Claim AI Classifier (Phase 2 — stub for now).
Classifies claim documents and assigns category/priority.

When AI keys are configured, this will call the LLM.
Until then, returns a deterministic mock result.
"""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_services.base import BaseAIService
from app.config import settings


class ClaimClassifier(BaseAIService):
    """
    Classifies a claim based on document text and context.

    AI Features (Phase 2):
    - Document type classification
    - Claim category assignment
    - Priority scoring
    - Missing document detection
    - Fraud signal detection
    """

    SERVICE_NAME = "claim_classifier"
    MODEL_NAME = settings.ai_model

    async def _call_model(
        self, masked_input: str, **kwargs
    ) -> tuple[Any, int | None, int | None]:
        """
        TODO (Phase 2): Replace stub with real LLM call.

        Will use LangChain with a structured output parser:
        {
            "category": str,
            "priority": "low|medium|high|critical",
            "fraud_score": float (0-1),
            "missing_documents": list[str],
            "summary": str
        }
        """
        if not settings.openai_api_key:
            # Return a mock result when no API key is configured
            return {
                "category": "hospitalization",
                "priority": "medium",
                "fraud_score": 0.05,
                "missing_documents": [],
                "summary": "[AI not configured — mock result]",
            }, None, None

        # Phase 2: Real LangChain implementation
        # from langchain_openai import ChatOpenAI
        # from langchain.output_parsers import PydanticOutputParser
        # ... real implementation here
        raise NotImplementedError("Phase 2 — AI not yet configured")


async def classify_claim(
    claim_text: str,
    db: AsyncSession,
    user_id: str | None = None,
    claim_id: str | None = None,
) -> dict:
    """
    Convenience function to classify a claim.

    Args:
        claim_text: Claim description + document text (PII will be auto-masked)
        db: DB session for audit logging
        user_id: For audit log
        claim_id: For audit log

    Returns:
        Classification result dict
    """
    classifier = ClaimClassifier(db)
    return await classifier.run(
        input_text=claim_text,
        user_id=user_id,
        resource_type="claim",
        resource_id=claim_id,
    )
