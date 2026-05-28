"""Employees router — /api/v1/employees/*"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Roles, get_current_user, require_roles
from app.core.response import paginated_response, success_response
from app.database import get_db
from app.modules.employees.repository import EmployeeRepository
from app.modules.employees.schemas import (
    EmployeeCreateRequest,
    EmployeeDetailResponse,
    EmployeeResponse,
    EmployeeUpdateRequest,
)
from app.modules.employees.service import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])


def get_service(db: AsyncSession = Depends(get_db)) -> EmployeeService:
    return EmployeeService(EmployeeRepository(db))


@router.get("/me", summary="Get my employee profile")
async def get_my_profile(
    current_user=Depends(get_current_user),
    service: EmployeeService = Depends(get_service),
):
    emp = await service.get_my_profile(current_user.id)
    return success_response(data=EmployeeDetailResponse.model_validate(emp))


@router.post("/", summary="Create employee profile (HR/Admin)")
async def create_employee(
    payload: EmployeeCreateRequest,
    current_user=Depends(require_roles(Roles.ADMIN_HR)),
    service: EmployeeService = Depends(get_service),
):
    emp = await service.create_employee(payload)
    return success_response(
        data=EmployeeDetailResponse.model_validate(emp),
        message="Employee profile created",
    )


@router.get("/", summary="List all employees (HR/Admin)")
async def list_employees(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user=Depends(require_roles(Roles.ADMIN_HR)),
    service: EmployeeService = Depends(get_service),
):
    emps, total = await service.list_employees(skip=skip, limit=limit)
    return paginated_response(
        data=[EmployeeResponse.model_validate(e) for e in emps],
        total=total, page=(skip // limit) + 1, page_size=limit,
    )


@router.get("/{employee_id}", summary="Get employee by ID")
async def get_employee(
    employee_id: str,
    current_user=Depends(require_roles(Roles.ADMIN_HR_INSURER)),
    service: EmployeeService = Depends(get_service),
):
    emp = await service.get_employee(employee_id)
    return success_response(data=EmployeeDetailResponse.model_validate(emp))


@router.put("/{employee_id}", summary="Update employee")
async def update_employee(
    employee_id: str,
    payload: EmployeeUpdateRequest,
    current_user=Depends(require_roles(Roles.ADMIN_HR)),
    service: EmployeeService = Depends(get_service),
):
    emp = await service.update_employee(employee_id, payload)
    return success_response(
        data=EmployeeDetailResponse.model_validate(emp),
        message="Employee updated",
    )
