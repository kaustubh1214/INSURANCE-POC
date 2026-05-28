"""Employee service — business logic."""
from app.core.exceptions import ConflictException, NotFoundException
from app.modules.employees.repository import EmployeeRepository
from app.modules.employees.schemas import EmployeeCreateRequest, EmployeeUpdateRequest


class EmployeeService:
    def __init__(self, repo: EmployeeRepository) -> None:
        self.repo = repo

    async def create_employee(self, payload: EmployeeCreateRequest):
        existing = await self.repo.get_by_code(payload.employee_code)
        if existing:
            raise ConflictException(
                f"Employee code '{payload.employee_code}' already exists"
            )
        return await self.repo.create(**payload.model_dump())

    async def get_employee(self, employee_id: str):
        emp = await self.repo.get_by_id(employee_id)
        if not emp:
            raise NotFoundException("Employee", employee_id)
        return emp

    async def get_my_profile(self, user_id: str):
        emp = await self.repo.get_by_user_id(user_id)
        if not emp:
            raise NotFoundException("Employee profile not found for this user")
        return emp

    async def update_employee(self, employee_id: str, payload: EmployeeUpdateRequest):
        emp = await self.get_employee(employee_id)
        return await self.repo.update(emp, **payload.model_dump(exclude_none=True))

    async def list_employees(self, skip: int = 0, limit: int = 50):
        return await self.repo.list_all(skip=skip, limit=limit)
