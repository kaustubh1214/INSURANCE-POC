"""Policy service."""
from app.core.exceptions import ConflictException, NotFoundException
from app.modules.policies.repository import EnrollmentRepository, PolicyRepository
from app.modules.policies.schemas import EnrollmentCreateRequest, PolicyCreateRequest
from app.modules.employees.repository import EmployeeRepository


class PolicyService:
    def __init__(self, repo: PolicyRepository, enrollment_repo: EnrollmentRepository) -> None:
        self.repo = repo
        self.enrollment_repo = enrollment_repo

    async def create_policy(self, payload: PolicyCreateRequest):
        return await self.repo.create(**payload.model_dump())

    async def get_policy(self, policy_id: str):
        policy = await self.repo.get_by_id(policy_id)
        if not policy:
            raise NotFoundException("Policy", policy_id)
        return policy

    async def list_policies(self, skip: int = 0, limit: int = 50):
        return await self.repo.list_all(skip=skip, limit=limit)

    async def enroll_employee(
        self,
        employee_id: str,
        payload: EnrollmentCreateRequest,
    ):
        policy = await self.get_policy(payload.policy_id)
        return await self.enrollment_repo.create(
            employee_id=employee_id,
            **payload.model_dump(),
        )

    async def get_my_enrollments(self, employee_id: str):
        return await self.enrollment_repo.list_by_employee(employee_id)
