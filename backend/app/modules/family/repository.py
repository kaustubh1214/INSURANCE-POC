"""Family Member repository."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.family.models import FamilyMember


class FamilyMemberRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, member_id: str) -> FamilyMember | None:
        result = await self.db.execute(
            select(FamilyMember).where(
                FamilyMember.id == member_id, FamilyMember.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def list_by_employee(self, employee_id: str) -> list[FamilyMember]:
        result = await self.db.execute(
            select(FamilyMember).where(
                FamilyMember.employee_id == employee_id,
                FamilyMember.is_active == True,
            )
        )
        return result.scalars().all()

    async def create(self, employee_id: str, **kwargs) -> FamilyMember:
        member = FamilyMember(employee_id=employee_id, **kwargs)
        self.db.add(member)
        await self.db.flush()
        return member

    async def update(self, member: FamilyMember, **kwargs) -> FamilyMember:
        for k, v in kwargs.items():
            setattr(member, k, v)
        await self.db.flush()
        return member

    async def soft_delete(self, member: FamilyMember) -> None:
        member.is_active = False
        await self.db.flush()
