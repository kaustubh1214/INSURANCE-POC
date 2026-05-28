"""Claims repository — data access for Claim, ClaimDocument, ClaimStatusHistory."""
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.claims.models import Claim, ClaimDocument, ClaimStatusHistory


class ClaimRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _generate_claim_number(self) -> str:
        """Generate a unique claim number: CLM-YYYYMMDD-XXXX"""
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")
        suffix = str(uuid.uuid4())[:6].upper()
        return f"CLM-{date_str}-{suffix}"

    async def get_by_id(self, claim_id: str) -> Claim | None:
        result = await self.db.execute(
            select(Claim).where(Claim.id == claim_id, Claim.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_by_claim_number(self, claim_number: str) -> Claim | None:
        result = await self.db.execute(
            select(Claim).where(Claim.claim_number == claim_number)
        )
        return result.scalar_one_or_none()

    async def list_by_employee(
        self, employee_id: str, skip: int = 0, limit: int = 50
    ) -> tuple[list[Claim], int]:
        result = await self.db.execute(
            select(Claim).where(
                Claim.employee_id == employee_id,
                Claim.is_active == True,
            )
        )
        all_claims = result.scalars().all()
        return all_claims[skip : skip + limit], len(all_claims)

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 50,
        status: str | None = None,
    ) -> tuple[list[Claim], int]:
        query = select(Claim).where(Claim.is_active == True)
        if status:
            query = query.where(Claim.status == status)
        result = await self.db.execute(query)
        all_claims = result.scalars().all()
        return all_claims[skip : skip + limit], len(all_claims)

    async def create(self, employee_id: str, **kwargs) -> Claim:
        claim = Claim(
            employee_id=employee_id,
            claim_number=self._generate_claim_number(),
            **kwargs,
        )
        self.db.add(claim)
        await self.db.flush()
        return claim

    async def update(self, claim: Claim, **kwargs) -> Claim:
        for k, v in kwargs.items():
            setattr(claim, k, v)
        await self.db.flush()
        return claim

    async def add_document(self, claim_id: str, **kwargs) -> ClaimDocument:
        doc = ClaimDocument(claim_id=claim_id, **kwargs)
        self.db.add(doc)
        await self.db.flush()
        return doc

    async def add_status_history(
        self,
        claim_id: str,
        from_status: str | None,
        to_status: str,
        changed_by_user_id: str | None = None,
        changed_by_name: str | None = None,
        change_reason: str | None = None,
        notes: str | None = None,
        is_system_action: bool = False,
    ) -> ClaimStatusHistory:
        history = ClaimStatusHistory(
            claim_id=claim_id,
            from_status=from_status,
            to_status=to_status,
            changed_by_user_id=changed_by_user_id,
            changed_by_name=changed_by_name,
            change_reason=change_reason,
            notes=notes,
            is_system_action=is_system_action,
        )
        self.db.add(history)
        await self.db.flush()
        return history

    async def get_status_history(self, claim_id: str) -> list[ClaimStatusHistory]:
        result = await self.db.execute(
            select(ClaimStatusHistory)
            .where(ClaimStatusHistory.claim_id == claim_id)
            .order_by(ClaimStatusHistory.changed_at)
        )
        return result.scalars().all()

    async def get_documents(self, claim_id: str) -> list[ClaimDocument]:
        result = await self.db.execute(
            select(ClaimDocument).where(
                ClaimDocument.claim_id == claim_id,
                ClaimDocument.is_active == True,
            )
        )
        return result.scalars().all()
