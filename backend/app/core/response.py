"""
Standardized API response envelope.
All API responses use this format for consistency.

Success: { "success": true, "data": {...}, "message": "...", "meta": {...} }
Error:   { "success": false, "data": null, "message": "...", "error_code": "...", "meta": {...} }
"""
import uuid
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Meta(BaseModel):
    """Pagination and request metadata."""

    request_id: str | None = None
    page: int | None = None
    page_size: int | None = None
    total: int | None = None
    total_pages: int | None = None


class APIResponse(BaseModel, Generic[T]):
    """
    Generic API response envelope.
    Use this as the return type for all endpoint functions.
    """

    success: bool
    data: T | None = None
    message: str = ""
    error_code: str | None = None
    meta: Meta | None = None


def success_response(
    data: Any = None,
    message: str = "Success",
    meta: Meta | None = None,
    request_id: str | None = None,
) -> dict:
    """
    Build a successful API response dict.

    Usage:
        return success_response(data=user_schema, message="User created")
    """
    response_meta = meta or Meta()
    response_meta.request_id = request_id or str(uuid.uuid4())

    return {
        "success": True,
        "data": data,
        "message": message,
        "error_code": None,
        "meta": response_meta.model_dump(exclude_none=True),
    }


def error_response(
    message: str,
    error_code: str = "ERROR",
    request_id: str | None = None,
) -> dict:
    """
    Build an error API response dict.
    Typically used in exception handlers.
    """
    return {
        "success": False,
        "data": None,
        "message": message,
        "error_code": error_code,
        "meta": {"request_id": request_id or str(uuid.uuid4())},
    }


def paginated_response(
    data: list,
    total: int,
    page: int,
    page_size: int,
    message: str = "Success",
    request_id: str | None = None,
) -> dict:
    """Build a paginated list response."""
    import math

    meta = Meta(
        request_id=request_id or str(uuid.uuid4()),
        page=page,
        page_size=page_size,
        total=total,
        total_pages=math.ceil(total / page_size) if page_size > 0 else 1,
    )
    return {
        "success": True,
        "data": data,
        "message": message,
        "error_code": None,
        "meta": meta.model_dump(exclude_none=True),
    }
