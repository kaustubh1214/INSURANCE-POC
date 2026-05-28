"""
Role-Based Access Control (RBAC) decorators and dependency factories.
Use these as FastAPI dependencies on protected routes.

Usage:
    @router.get("/admin-only")
    async def admin_endpoint(
        current_user: User = Depends(require_roles(["admin"]))
    ):
        ...

    @router.get("/employee-or-hr")
    async def shared_endpoint(
        current_user: User = Depends(require_roles(["employee", "hr", "admin"]))
    ):
        ...
"""
from typing import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.database import get_db

# HTTP Bearer token extractor
bearer_scheme = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Allowed Roles
# ---------------------------------------------------------------------------
class Roles:
    ADMIN = "admin"
    HR = "hr"
    EMPLOYEE = "employee"
    INSURER = "insurer"
    AGENT = "agent"

    # Convenience groups
    ADMIN_ONLY = [ADMIN]
    ADMIN_HR = [ADMIN, HR]
    ADMIN_INSURER = [ADMIN, INSURER]
    ADMIN_HR_INSURER = [ADMIN, HR, INSURER]
    ALL_ROLES = [ADMIN, HR, EMPLOYEE, INSURER, AGENT]


# ---------------------------------------------------------------------------
# Current User Dependency
# ---------------------------------------------------------------------------
async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    FastAPI dependency: extracts and validates JWT, returns current User.
    Raises UnauthorizedException if token is missing or invalid.
    """
    if credentials is None:
        raise UnauthorizedException(detail="Bearer token required")

    payload = decode_access_token(credentials.credentials)
    user_id: str | None = payload.get("sub")

    if not user_id:
        raise UnauthorizedException(detail="Invalid token payload")

    # Import here to avoid circular imports
    from app.modules.users.repository import UserRepository

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)

    if not user:
        raise UnauthorizedException(detail="User not found")

    if not user.is_active:
        raise UnauthorizedException(detail="Account deactivated")

    return user


# ---------------------------------------------------------------------------
# Role-Based Dependency Factory
# ---------------------------------------------------------------------------
def require_roles(allowed_roles: list[str]) -> Callable:
    """
    Dependency factory that enforces role-based access.

    Args:
        allowed_roles: List of roles permitted to access the endpoint.

    Returns:
        A FastAPI dependency function that yields the current user if authorized.

    Example:
        Depends(require_roles([Roles.ADMIN, Roles.HR]))
    """

    async def _check_roles(
        current_user=Depends(get_current_user),
    ):
        if current_user.role not in allowed_roles:
            raise ForbiddenException(
                detail=f"Role '{current_user.role}' is not permitted. "
                f"Required: {allowed_roles}"
            )
        return current_user

    return _check_roles


def require_admin():
    """Shortcut: admin only."""
    return Depends(require_roles(Roles.ADMIN_ONLY))


def require_admin_or_hr():
    """Shortcut: admin or HR."""
    return Depends(require_roles(Roles.ADMIN_HR))


def require_any_authenticated():
    """Shortcut: any logged-in user (all roles)."""
    return Depends(get_current_user)
