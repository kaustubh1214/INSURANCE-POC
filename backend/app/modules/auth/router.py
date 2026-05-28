"""
Auth router — /api/v1/auth/* endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import get_current_user
from app.core.response import success_response
from app.database import get_db
from app.modules.auth.schemas import (
    CurrentUserResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.modules.auth.service import AuthService
from app.modules.users.repository import UserRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


@router.post("/register", summary="Register a new user account")
async def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
):
    """
    Register a new user.
    - Validates email uniqueness
    - Hashes password with bcrypt
    - Returns created user info (no token — must login separately)
    """
    user = await service.register(payload)
    return success_response(
        data=CurrentUserResponse.model_validate(user),
        message="Registration successful. Please login.",
    )


@router.post("/login", response_model=None, summary="Login and obtain JWT tokens")
async def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    """
    Authenticate user.
    Returns access_token (30 min) and refresh_token (7 days).
    """
    tokens = await service.login(payload)
    return success_response(
        data=tokens.model_dump(),
        message="Login successful",
    )


@router.post("/refresh", summary="Refresh access token")
async def refresh(
    payload: RefreshRequest,
    service: AuthService = Depends(get_auth_service),
):
    """
    Rotate tokens using a valid refresh token.
    Both access and refresh tokens are reissued (refresh token rotation).
    """
    tokens = await service.refresh(payload.refresh_token)
    return success_response(
        data=tokens.model_dump(),
        message="Tokens refreshed",
    )


@router.post("/logout", summary="Logout and invalidate refresh token")
async def logout(
    current_user=Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    """Invalidate the current user's refresh token."""
    await service.logout(current_user.id)
    return success_response(message="Logged out successfully")


@router.get("/me", summary="Get current authenticated user")
async def get_me(current_user=Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return success_response(
        data=CurrentUserResponse.model_validate(current_user),
        message="Current user retrieved",
    )
