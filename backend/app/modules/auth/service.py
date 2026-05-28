"""
Authentication service — business logic for login, registration, token refresh.
"""
from app.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.modules.users.repository import UserRepository


class AuthService:
    """Handles registration, login, and token management."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register(self, payload: RegisterRequest):
        """
        Register a new user.
        Raises ConflictException if email already exists.
        """
        existing = await self.user_repo.get_by_email(payload.email)
        if existing:
            raise ConflictException(
                detail=f"Email '{payload.email}' is already registered"
            )

        hashed = hash_password(payload.password)
        user = await self.user_repo.create(
            email=payload.email,
            hashed_password=hashed,
            full_name=payload.full_name,
            phone=payload.phone,
            role=payload.role,
            is_verified=False,
        )
        return user

    async def login(self, payload: LoginRequest) -> TokenResponse:
        """
        Authenticate user and return JWT token pair.
        Raises UnauthorizedException on bad credentials.
        """
        user = await self.user_repo.get_by_email(payload.email)

        # Use constant-time comparison to prevent timing attacks
        if not user or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedException(detail="Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException(detail="Account is deactivated")

        # Build extra claims for access token
        extra_claims = {
            "email": user.email,
            "name": user.full_name,
        }

        access_token = create_access_token(
            subject=user.id,
            role=user.role,
            extra_claims=extra_claims,
        )
        refresh_token = create_refresh_token(subject=user.id)

        # Persist refresh token for invalidation support
        await self.user_repo.update_refresh_token(user, refresh_token)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """
        Issue new access token using a valid refresh token.
        Validates the stored token matches (prevents token reuse after logout).
        """
        payload = decode_refresh_token(refresh_token)
        user_id: str = payload.get("sub", "")

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedException(detail="User not found")

        # Verify stored token matches (rotation security)
        if user.refresh_token != refresh_token:
            raise UnauthorizedException(detail="Refresh token has been invalidated")

        extra_claims = {"email": user.email, "name": user.full_name}
        new_access_token = create_access_token(
            subject=user.id,
            role=user.role,
            extra_claims=extra_claims,
        )
        new_refresh_token = create_refresh_token(subject=user.id)

        # Rotate refresh token
        await self.user_repo.update_refresh_token(user, new_refresh_token)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    async def logout(self, user_id: str) -> None:
        """Invalidate the user's refresh token."""
        user = await self.user_repo.get_by_id(user_id)
        if user:
            await self.user_repo.update_refresh_token(user, None)
