"""
Custom exception classes for the application.
Centralizing exceptions allows consistent error handling and HTTP mapping.
"""
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception. All custom exceptions extend this."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = "APP_ERROR",
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class UnauthorizedException(AppException):
    """401 — Authentication required or token invalid."""

    def __init__(self, detail: str = "Authentication required") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="UNAUTHORIZED",
        )


class ForbiddenException(AppException):
    """403 — Authenticated but not permitted."""

    def __init__(self, detail: str = "You don't have permission to perform this action") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="FORBIDDEN",
        )


class NotFoundException(AppException):
    """404 — Resource not found."""

    def __init__(self, resource: str = "Resource", resource_id: str | None = None) -> None:
        detail = f"{resource} not found"
        if resource_id:
            detail = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND",
        )


class ConflictException(AppException):
    """409 — Resource already exists or state conflict."""

    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT",
        )


class ValidationException(AppException):
    """422 — Business rule validation failed."""

    def __init__(self, detail: str = "Validation failed") -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
        )


class BadRequestException(AppException):
    """400 — Malformed request."""

    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="BAD_REQUEST",
        )


class ClaimWorkflowException(ValidationException):
    """Invalid claim status transition."""

    def __init__(self, from_status: str, to_status: str) -> None:
        super().__init__(
            detail=f"Cannot transition claim from '{from_status}' to '{to_status}'"
        )
        self.error_code = "INVALID_CLAIM_TRANSITION"


class FileSizeException(BadRequestException):
    """Uploaded file exceeds maximum allowed size."""

    def __init__(self, max_mb: int) -> None:
        super().__init__(detail=f"File exceeds maximum allowed size of {max_mb}MB")
        self.error_code = "FILE_TOO_LARGE"


class FileTypeException(BadRequestException):
    """Uploaded file type not allowed."""

    def __init__(self, allowed_types: list[str]) -> None:
        super().__init__(
            detail=f"File type not allowed. Allowed: {', '.join(allowed_types)}"
        )
        self.error_code = "INVALID_FILE_TYPE"
