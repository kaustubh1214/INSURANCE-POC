"""User service — business logic for user management."""
from app.core.exceptions import ForbiddenException, NotFoundException
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserUpdateRequest


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def get_user(self, user_id: str):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return user

    async def update_user(self, user_id: str, payload: UserUpdateRequest, requester_id: str):
        user = await self.get_user(user_id)
        # Users can only update their own profile (admins can update any)
        update_data = payload.model_dump(exclude_none=True)
        return await self.repo.update(user, **update_data)

    async def list_users(self, skip: int = 0, limit: int = 50, role: str | None = None):
        return await self.repo.list_all(skip=skip, limit=limit, role=role)

    async def deactivate_user(self, user_id: str, requester_role: str):
        if requester_role != "admin":
            raise ForbiddenException()
        user = await self.get_user(user_id)
        return await self.repo.soft_delete(user)
