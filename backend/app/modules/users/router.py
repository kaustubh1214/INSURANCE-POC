"""Users router — /api/v1/users/* endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Roles, get_current_user, require_roles
from app.core.response import paginated_response, success_response
from app.database import get_db
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserResponse, UserUpdateRequest
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


@router.get("/", summary="List all users (Admin only)")
async def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    role: str | None = Query(default=None),
    current_user=Depends(require_roles(Roles.ADMIN_ONLY)),
    service: UserService = Depends(get_service),
):
    users, total = await service.list_users(skip=skip, limit=limit, role=role)
    return paginated_response(
        data=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
    )


@router.get("/{user_id}", summary="Get user by ID")
async def get_user(
    user_id: str,
    current_user=Depends(require_roles(Roles.ADMIN_HR)),
    service: UserService = Depends(get_service),
):
    user = await service.get_user(user_id)
    return success_response(data=UserResponse.model_validate(user))


@router.put("/{user_id}", summary="Update user profile")
async def update_user(
    user_id: str,
    payload: UserUpdateRequest,
    current_user=Depends(get_current_user),
    service: UserService = Depends(get_service),
):
    # Employees can update their own; admins can update anyone
    if current_user.role not in Roles.ADMIN_ONLY and current_user.id != user_id:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException()

    user = await service.update_user(user_id, payload, current_user.id)
    return success_response(
        data=UserResponse.model_validate(user),
        message="User updated successfully",
    )


@router.delete("/{user_id}", summary="Deactivate user (Admin only)")
async def deactivate_user(
    user_id: str,
    current_user=Depends(require_roles(Roles.ADMIN_ONLY)),
    service: UserService = Depends(get_service),
):
    await service.deactivate_user(user_id, current_user.role)
    return success_response(message="User deactivated successfully")
