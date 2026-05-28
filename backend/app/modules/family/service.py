"""Family Member service."""
from app.core.exceptions import ForbiddenException, NotFoundException
from app.modules.family.repository import FamilyMemberRepository
from app.modules.family.schemas import FamilyMemberCreateRequest, FamilyMemberUpdateRequest
from app.modules.employees.repository import EmployeeRepository


class FamilyMemberService:
    def __init__(
        self,
        repo: FamilyMemberRepository,
        emp_repo: EmployeeRepository,
    ) -> None:
        self.repo = repo
        self.emp_repo = emp_repo

    async def _get_employee_or_raise(self, user_id: str):
        emp = await self.emp_repo.get_by_user_id(user_id)
        if not emp:
            raise NotFoundException("Employee profile")
        return emp

    async def add_member(
        self, user_id: str, payload: FamilyMemberCreateRequest
    ):
        emp = await self._get_employee_or_raise(user_id)
        return await self.repo.create(
            employee_id=emp.id, **payload.model_dump()
        )

    async def list_my_members(self, user_id: str):
        emp = await self._get_employee_or_raise(user_id)
        return await self.repo.list_by_employee(emp.id)

    async def update_member(
        self,
        member_id: str,
        payload: FamilyMemberUpdateRequest,
        user_id: str,
    ):
        member = await self.repo.get_by_id(member_id)
        if not member:
            raise NotFoundException("Family member", member_id)
        # Ensure requester owns this member
        emp = await self._get_employee_or_raise(user_id)
        if member.employee_id != emp.id:
            raise ForbiddenException()
        return await self.repo.update(member, **payload.model_dump(exclude_none=True))

    async def delete_member(self, member_id: str, user_id: str):
        member = await self.repo.get_by_id(member_id)
        if not member:
            raise NotFoundException("Family member", member_id)
        emp = await self._get_employee_or_raise(user_id)
        if member.employee_id != emp.id:
            raise ForbiddenException()
        await self.repo.soft_delete(member)
