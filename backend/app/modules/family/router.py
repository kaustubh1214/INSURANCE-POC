"""Family Members router — /api/v1/family/*"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import get_current_user
from app.core.response import success_response
from app.database import get_db
from app.modules.employees.repository import EmployeeRepository
from app.modules.family.repository import FamilyMemberRepository
from app.modules.family.schemas import (
    FamilyMemberCreateRequest,
    FamilyMemberResponse,
    FamilyMemberUpdateRequest,
)
from app.modules.family.service import FamilyMemberService

router = APIRouter(prefix="/family", tags=["Family Members"])


def get_service(db: AsyncSession = Depends(get_db)) -> FamilyMemberService:
    return FamilyMemberService(FamilyMemberRepository(db), EmployeeRepository(db))


@router.get("/", summary="List my family members")
async def list_my_family(
    current_user=Depends(get_current_user),
    service: FamilyMemberService = Depends(get_service),
):
    members = await service.list_my_members(current_user.id)
    return success_response(
        data=[FamilyMemberResponse.model_validate(m) for m in members]
    )


@router.post("/", summary="Add a family member")
async def add_family_member(
    payload: FamilyMemberCreateRequest,
    current_user=Depends(get_current_user),
    service: FamilyMemberService = Depends(get_service),
):
    member = await service.add_member(current_user.id, payload)
    return success_response(
        data=FamilyMemberResponse.model_validate(member),
        message="Family member added",
    )


@router.put("/{member_id}", summary="Update a family member")
async def update_family_member(
    member_id: str,
    payload: FamilyMemberUpdateRequest,
    current_user=Depends(get_current_user),
    service: FamilyMemberService = Depends(get_service),
):
    member = await service.update_member(member_id, payload, current_user.id)
    return success_response(
        data=FamilyMemberResponse.model_validate(member),
        message="Family member updated",
    )


@router.delete("/{member_id}", summary="Remove a family member")
async def delete_family_member(
    member_id: str,
    current_user=Depends(get_current_user),
    service: FamilyMemberService = Depends(get_service),
):
    await service.delete_member(member_id, current_user.id)
    return success_response(message="Family member removed")
