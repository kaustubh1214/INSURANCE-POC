"""
Claims service — business logic for claim lifecycle management.
Enforces the claim status state machine.
"""
import os
from datetime import datetime, timezone

from fastapi import UploadFile

from app.config import settings
from app.core.audit import write_audit_log
from app.core.exceptions import (
    ClaimWorkflowException,
    FileTypeException,
    FileSizeException,
    ForbiddenException,
    NotFoundException,
)
from app.modules.claims.models import ClaimStatus
from app.modules.claims.repository import ClaimRepository
from app.modules.claims.schemas import ClaimCreateRequest, ClaimStatusUpdateRequest
from app.modules.employees.repository import EmployeeRepository
from sqlalchemy.ext.asyncio import AsyncSession


class ClaimService:
    def __init__(
        self,
        repo: ClaimRepository,
        emp_repo: EmployeeRepository,
        db: AsyncSession,
    ) -> None:
        self.repo = repo
        self.emp_repo = emp_repo
        self.db = db

    async def _get_employee(self, user_id: str):
        emp = await self.emp_repo.get_by_user_id(user_id)
        if not emp:
            raise NotFoundException("Employee profile")
        return emp

    def _validate_transition(self, from_status: str, to_status: str) -> None:
        """Enforce the claim status state machine."""
        allowed = ClaimStatus.TRANSITIONS.get(from_status, [])
        if to_status not in allowed:
            raise ClaimWorkflowException(from_status, to_status)

    async def create_claim(
        self, user_id: str, payload: ClaimCreateRequest
    ):
        """Initiate a new claim (starts in DRAFT status)."""
        emp = await self._get_employee(user_id)

        claim = await self.repo.create(
            employee_id=emp.id,
            **payload.model_dump(),
        )

        # Record initial status history
        await self.repo.add_status_history(
            claim_id=claim.id,
            from_status=None,
            to_status=ClaimStatus.DRAFT,
            is_system_action=True,
            notes="Claim initiated by employee",
        )

        await write_audit_log(
            self.db,
            action="CREATE_CLAIM",
            resource_type="claim",
            resource_id=claim.id,
            user_id=user_id,
            new_value={"claim_number": claim.claim_number, "status": claim.status},
        )

        return claim

    async def submit_claim(self, claim_id: str, user_id: str):
        """Submit a DRAFT claim for processing."""
        claim = await self._get_claim_for_user(claim_id, user_id)

        self._validate_transition(claim.status, ClaimStatus.SUBMITTED)
        old_status = claim.status

        emp = await self._get_employee(user_id)
        claim = await self.repo.update(
            claim,
            status=ClaimStatus.SUBMITTED,
            submitted_at=datetime.now(timezone.utc),
        )

        await self.repo.add_status_history(
            claim_id=claim.id,
            from_status=old_status,
            to_status=ClaimStatus.SUBMITTED,
            changed_by_user_id=user_id,
            notes="Submitted by employee",
        )

        await write_audit_log(
            self.db,
            action="SUBMIT_CLAIM",
            resource_type="claim",
            resource_id=claim.id,
            user_id=user_id,
            old_value={"status": old_status},
            new_value={"status": claim.status},
        )

        return claim

    async def update_claim_status(
        self,
        claim_id: str,
        payload: ClaimStatusUpdateRequest,
        current_user,
    ):
        """
        Update claim status (insurer/admin action).
        Enforces state machine transitions.
        """
        claim = await self.repo.get_by_id(claim_id)
        if not claim:
            raise NotFoundException("Claim", claim_id)

        # Only admin/insurer can update status
        if current_user.role not in ["admin", "insurer", "hr"]:
            raise ForbiddenException()

        self._validate_transition(claim.status, payload.status)
        old_status = claim.status

        update_data = {"status": payload.status}
        if payload.approved_amount is not None:
            update_data["approved_amount"] = payload.approved_amount
        if payload.rejection_reason:
            update_data["rejection_reason"] = payload.rejection_reason

        claim = await self.repo.update(claim, **update_data)

        await self.repo.add_status_history(
            claim_id=claim.id,
            from_status=old_status,
            to_status=payload.status,
            changed_by_user_id=current_user.id,
            changed_by_name=current_user.full_name,
            change_reason=payload.change_reason,
            notes=payload.notes,
        )

        await write_audit_log(
            self.db,
            action=f"UPDATE_CLAIM_STATUS_{payload.status.upper()}",
            resource_type="claim",
            resource_id=claim.id,
            user_id=current_user.id,
            user_email=current_user.email,
            user_role=current_user.role,
            old_value={"status": old_status},
            new_value={"status": payload.status},
        )

        return claim

    async def upload_document(
        self,
        claim_id: str,
        document_type: str,
        file: UploadFile,
        user_id: str,
    ):
        """Upload a document to a claim."""
        claim = await self._get_claim_for_user(claim_id, user_id)

        # Validate file type
        ext = os.path.splitext(file.filename or "")[1].lstrip(".").lower()
        if ext not in settings.allowed_extensions:
            raise FileTypeException(settings.allowed_extensions)

        # Read and check size
        content = await file.read()
        size_kb = len(content) // 1024
        if size_kb > settings.max_file_size_mb * 1024:
            raise FileSizeException(settings.max_file_size_mb)

        # Save file
        upload_dir = os.path.join(settings.upload_dir, "claims", claim_id)
        os.makedirs(upload_dir, exist_ok=True)
        import uuid as _uuid
        safe_name = f"{_uuid.uuid4()}.{ext}"
        file_path = os.path.join(upload_dir, safe_name)
        with open(file_path, "wb") as f:
            f.write(content)

        doc = await self.repo.add_document(
            claim_id=claim_id,
            document_type=document_type,
            file_name=file.filename or safe_name,
            file_path=file_path,
            file_size_kb=size_kb,
            mime_type=file.content_type,
            uploaded_by_user_id=user_id,
            ocr_status="pending",
        )

        return doc

    async def get_claim(self, claim_id: str, current_user):
        """Get claim details — employees can only see their own."""
        claim = await self.repo.get_by_id(claim_id)
        if not claim:
            raise NotFoundException("Claim", claim_id)

        # Employees can only access their own claims
        if current_user.role == "employee":
            emp = await self._get_employee(current_user.id)
            if claim.employee_id != emp.id:
                raise ForbiddenException()

        return claim

    async def list_my_claims(
        self, user_id: str, skip: int = 0, limit: int = 50
    ):
        emp = await self._get_employee(user_id)
        return await self.repo.list_by_employee(emp.id, skip=skip, limit=limit)

    async def list_all_claims(
        self,
        skip: int = 0,
        limit: int = 50,
        status: str | None = None,
    ):
        return await self.repo.list_all(skip=skip, limit=limit, status=status)

    async def get_claim_timeline(self, claim_id: str):
        """Get full status history for a claim."""
        return await self.repo.get_status_history(claim_id)

    async def get_claim_documents(self, claim_id: str):
        return await self.repo.get_documents(claim_id)

    async def _get_claim_for_user(self, claim_id: str, user_id: str):
        """Get claim and verify the user owns it."""
        claim = await self.repo.get_by_id(claim_id)
        if not claim:
            raise NotFoundException("Claim", claim_id)
        emp = await self._get_employee(user_id)
        if claim.employee_id != emp.id:
            raise ForbiddenException()
        return claim
