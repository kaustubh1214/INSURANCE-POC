"""
Security utilities: JWT creation/verification, password hashing.
All cryptographic operations centralized here — never scattered across modules.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.core.exceptions import UnauthorizedException

# ---------------------------------------------------------------------------
# Password Hashing
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT Token Management
# ---------------------------------------------------------------------------
def create_access_token(
    subject: str,
    role: str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a short-lived JWT access token.

    Args:
        subject: User UUID (stored as 'sub' claim)
        role: User role (stored as 'role' claim)
        extra_claims: Any additional data to embed in the token

    Returns:
        Signed JWT string
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": expire,
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(subject: str) -> str:
    """
    Create a long-lived JWT refresh token.

    Args:
        subject: User UUID

    Returns:
        Signed JWT string
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.refresh_token_expire_days)

    payload: dict[str, Any] = {
        "sub": subject,
        "type": "refresh",
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT token.

    Raises:
        UnauthorizedException: If token is invalid, expired, or malformed.

    Returns:
        Decoded token payload dict
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as exc:
        raise UnauthorizedException(detail=f"Invalid token: {exc}") from exc


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate an access token (checks type claim)."""
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise UnauthorizedException(detail="Not an access token")
    return payload


def decode_refresh_token(token: str) -> dict[str, Any]:
    """Decode and validate a refresh token (checks type claim)."""
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise UnauthorizedException(detail="Not a refresh token")
    return payload
