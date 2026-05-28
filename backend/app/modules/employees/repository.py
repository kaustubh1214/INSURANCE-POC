"""Employee repository — DB access for Employee model."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.employees.models import Employee


class EmployeeRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, employee_id: str) -> Employee | None:
        result = await self.db.execute(
            select(Employee).where(
                Employee.id == employee_id, Employee.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> Employee | None:
        result = await self.db.execute(
            select(Employee).where(
                Employee.user_id == user_id, Employee.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Employee | None:
        result = await self.db.execute(
            select(Employee).where(Employee.employee_code == code)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> Employee:
        emp = Employee(**kwargs)
        self.db.add(emp)
        await self.db.flush()
        return emp

    async def update(self, emp: Employee, **kwargs) -> Employee:
        for k, v in kwargs.items():
            setattr(emp, k, v)
        await self.db.flush()
        return emp

    async def list_all(
        self, skip: int = 0, limit: int = 50
    ) -> tuple[list[Employee], int]:
        result = await self.db.execute(
            select(Employee).where(Employee.is_active == True)
        )
        all_emps = result.scalars().all()
        total = len(all_emps)
        return all_emps[skip : skip + limit], total
