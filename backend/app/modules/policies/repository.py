"""Policy and PolicyEnrollment repository."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.policies.models import Policy, PolicyEnrollment


class PolicyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, policy_id: str) -> Policy | None:
        result = await self.db.execute(
            select(Policy).where(Policy.id == policy_id, Policy.is_active == True)
        )
        return result.scalar_one_or_none()

    async def list_all(self, skip: int = 0, limit: int = 50):
        result = await self.db.execute(
            select(Policy).where(Policy.is_active == True).offset(skip).limit(limit)
        )
        policies = result.scalars().all()
        return policies, len(policies)

    async def create(self, **kwargs) -> Policy:
        policy = Policy(**kwargs)
        self.db.add(policy)
        await self.db.flush()
        return policy


class EnrollmentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, enrollment_id: str) -> PolicyEnrollment | None:
        result = await self.db.execute(
            select(PolicyEnrollment).where(PolicyEnrollment.id == enrollment_id)
        )
        return result.scalar_one_or_none()

    async def list_by_employee(self, employee_id: str) -> list[PolicyEnrollment]:
        result = await self.db.execute(
            select(PolicyEnrollment).where(
                PolicyEnrollment.employee_id == employee_id,
                PolicyEnrollment.is_active == True,
            )
        )
        return result.scalars().all()

    async def create(self, **kwargs) -> PolicyEnrollment:
        enrollment = PolicyEnrollment(**kwargs)
        self.db.add(enrollment)
        await self.db.flush()
        return enrollment
