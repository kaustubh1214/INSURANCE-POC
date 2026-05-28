"""Policies router — /api/v1/policies/*"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Roles, get_current_user, require_roles
from app.core.response import paginated_response, success_response
from app.database import get_db
from app.modules.employees.repository import EmployeeRepository
from app.modules.policies.repository import EnrollmentRepository, PolicyRepository
from app.modules.policies.schemas import (
    EnrollmentCreateRequest,
    EnrollmentResponse,
    PolicyCreateRequest,
    PolicyResponse,
)
from app.modules.policies.service import PolicyService

router = APIRouter(prefix="/policies", tags=["Policies"])


def get_service(db: AsyncSession = Depends(get_db)) -> PolicyService:
    return PolicyService(PolicyRepository(db), EnrollmentRepository(db))


@router.get("/", summary="List all available policies")
async def list_policies(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user=Depends(get_current_user),
    service: PolicyService = Depends(get_service),
):
    policies, total = await service.list_policies(skip=skip, limit=limit)
    return paginated_response(
        data=[PolicyResponse.model_validate(p) for p in policies],
        total=total, page=(skip // limit) + 1, page_size=limit,
    )


@router.post("/", summary="Create a new policy (Admin/Insurer)")
async def create_policy(
    payload: PolicyCreateRequest,
    current_user=Depends(require_roles(Roles.ADMIN_INSURER)),
    service: PolicyService = Depends(get_service),
):
    policy = await service.create_policy(payload)
    return success_response(
        data=PolicyResponse.model_validate(policy),
        message="Policy created",
    )


@router.get("/my-policies", summary="Get my enrolled policies")
async def get_my_policies(
    current_user=Depends(get_current_user),
    service: PolicyService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
):
    emp_repo = EmployeeRepository(db)
    emp = await emp_repo.get_by_user_id(current_user.id)
    if not emp:
        return success_response(data=[], message="No employee profile found")
    enrollments = await service.get_my_enrollments(emp.id)
    return success_response(
        data=[EnrollmentResponse.model_validate(e) for e in enrollments]
    )


@router.get("/{policy_id}", summary="Get policy details")
async def get_policy(
    policy_id: str,
    current_user=Depends(get_current_user),
    service: PolicyService = Depends(get_service),
):
    policy = await service.get_policy(policy_id)
    return success_response(data=PolicyResponse.model_validate(policy))


@router.post("/{policy_id}/enroll", summary="Enroll in a policy")
async def enroll_in_policy(
    policy_id: str,
    payload: EnrollmentCreateRequest,
    current_user=Depends(get_current_user),
    service: PolicyService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
):
    emp_repo = EmployeeRepository(db)
    emp = await emp_repo.get_by_user_id(current_user.id)
    if not emp:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Employee profile")
    enrollment = await service.enroll_employee(emp.id, payload)
    return success_response(
        data=EnrollmentResponse.model_validate(enrollment),
        message="Enrolled in policy",
    )
