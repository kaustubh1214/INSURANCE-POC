"""
Claims router — /api/v1/claims/*
Full claim intimation workflow: initiate → upload docs → submit → review → settle.
"""
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Roles, get_current_user, require_roles
from app.core.response import paginated_response, success_response
from app.database import get_db
from app.modules.claims.repository import ClaimRepository
from app.modules.claims.schemas import (
    ClaimCreateRequest,
    ClaimDocumentResponse,
    ClaimResponse,
    ClaimStatusHistoryResponse,
    ClaimStatusUpdateRequest,
)
from app.modules.claims.service import ClaimService
from app.modules.employees.repository import EmployeeRepository

router = APIRouter(prefix="/claims", tags=["Claims"])


def get_service(db: AsyncSession = Depends(get_db)) -> ClaimService:
    return ClaimService(ClaimRepository(db), EmployeeRepository(db), db)


# ---------------------------------------------------------------------------
# Employee Endpoints
# ---------------------------------------------------------------------------

@router.post("/", summary="Initiate a new claim")
async def create_claim(
    payload: ClaimCreateRequest,
    current_user=Depends(get_current_user),
    service: ClaimService = Depends(get_service),
):
    """
    Start a claim in DRAFT status.
    Employee must have an active policy enrollment.
    """
    claim = await service.create_claim(current_user.id, payload)
    return success_response(
        data=ClaimResponse.model_validate(claim),
        message=f"Claim {claim.claim_number} initiated",
    )


@router.get("/", summary="List claims (mine or all for admin/insurer)")
async def list_claims(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    status: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    service: ClaimService = Depends(get_service),
):
    if current_user.role in ["admin", "insurer", "hr"]:
        claims, total = await service.list_all_claims(
            skip=skip, limit=limit, status=status
        )
    else:
        claims, total = await service.list_my_claims(
            user_id=current_user.id, skip=skip, limit=limit
        )

    return paginated_response(
        data=[ClaimResponse.model_validate(c) for c in claims],
        total=total, page=(skip // limit) + 1, page_size=limit,
    )


@router.get("/{claim_id}", summary="Get claim details")
async def get_claim(
    claim_id: str,
    current_user=Depends(get_current_user),
    service: ClaimService = Depends(get_service),
):
    claim = await service.get_claim(claim_id, current_user)
    return success_response(data=ClaimResponse.model_validate(claim))


@router.post("/{claim_id}/submit", summary="Submit a draft claim")
async def submit_claim(
    claim_id: str,
    current_user=Depends(get_current_user),
    service: ClaimService = Depends(get_service),
):
    """Move claim from DRAFT → SUBMITTED."""
    claim = await service.submit_claim(claim_id, current_user.id)
    return success_response(
        data=ClaimResponse.model_validate(claim),
        message="Claim submitted for review",
    )


@router.post("/{claim_id}/documents", summary="Upload a document to a claim")
async def upload_document(
    claim_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    service: ClaimService = Depends(get_service),
):
    """
    Upload supporting document (bill, prescription, discharge summary, etc.)
    Triggers async OCR processing.
    """
    doc = await service.upload_document(
        claim_id=claim_id,
        document_type=document_type,
        file=file,
        user_id=current_user.id,
    )
    return success_response(
        data=ClaimDocumentResponse.model_validate(doc),
        message="Document uploaded. OCR processing will begin shortly.",
    )


@router.get("/{claim_id}/documents", summary="List claim documents")
async def list_documents(
    claim_id: str,
    current_user=Depends(get_current_user),
    service: ClaimService = Depends(get_service),
):
    await service.get_claim(claim_id, current_user)  # Auth check
    docs = await service.get_claim_documents(claim_id)
    return success_response(
        data=[ClaimDocumentResponse.model_validate(d) for d in docs]
    )


@router.get("/{claim_id}/timeline", summary="Get claim status history / audit trail")
async def get_claim_timeline(
    claim_id: str,
    current_user=Depends(get_current_user),
    service: ClaimService = Depends(get_service),
):
    """Returns the full chronological audit trail of status changes for this claim."""
    await service.get_claim(claim_id, current_user)  # Auth check
    history = await service.get_claim_timeline(claim_id)
    return success_response(
        data=[ClaimStatusHistoryResponse.model_validate(h) for h in history]
    )


# ---------------------------------------------------------------------------
# Admin / Insurer Endpoints
# ---------------------------------------------------------------------------

@router.put("/{claim_id}/status", summary="Update claim status (Admin/Insurer)")
async def update_claim_status(
    claim_id: str,
    payload: ClaimStatusUpdateRequest,
    current_user=Depends(require_roles(Roles.ADMIN_HR_INSURER)),
    service: ClaimService = Depends(get_service),
):
    """
    Transition claim status.
    State machine:
    DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED → SETTLED
                                    ↘ REJECTED
    """
    claim = await service.update_claim_status(claim_id, payload, current_user)
    return success_response(
        data=ClaimResponse.model_validate(claim),
        message=f"Claim status updated to {payload.status}",
    )
