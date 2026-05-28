"""
User repository — all database operations for the User model.
No business logic here, only data access.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User


class UserRepository:
    """Data access layer for User entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> User:
        if "email" in kwargs:
            kwargs["email"] = kwargs["email"].lower()
        user = User(**kwargs)
        self.db.add(user)
        await self.db.flush()  # Get the ID without committing
        return user

    async def update(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            setattr(user, key, value)
        await self.db.flush()
        return user

    async def soft_delete(self, user: User) -> User:
        user.is_active = False
        await self.db.flush()
        return user

    async def list_all(
        self, skip: int = 0, limit: int = 50, role: str | None = None
    ) -> tuple[list[User], int]:
        query = select(User).where(User.is_active == True)
        if role:
            query = query.where(User.role == role)

        count_result = await self.db.execute(
            select(User).where(User.is_active == True)
        )
        total = len(count_result.scalars().all())

        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all(), total

    async def update_refresh_token(
        self, user: User, refresh_token: str | None
    ) -> User:
        user.refresh_token = refresh_token
        await self.db.flush()
        return user
