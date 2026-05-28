"""Tickets router — /api/v1/tickets/*"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Roles, get_current_user, require_roles
from app.core.response import success_response
from app.database import get_db
from app.modules.tickets.models import Ticket

router = APIRouter(prefix="/tickets", tags=["Support Tickets"])


def _ticket_dict(t: Ticket) -> dict:
    return {
        "id":                       t.id,
        "ticket_number":            t.ticket_number,
        "subject":                  t.subject,
        "description":              t.description,
        "category":                 t.category,
        "priority":                 t.priority,
        "status":                   t.status,
        "ai_auto_resolved":         t.ai_auto_resolved,
        "ai_resolution_suggestion": t.ai_resolution_suggestion,
        "satisfaction_rating":      t.satisfaction_rating,
        "created_at":               t.created_at.isoformat(),
        "resolved_at":              t.resolved_at.isoformat() if t.resolved_at else None,
    }


@router.get("/", summary="List my tickets")
async def list_my_tickets(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Ticket)
        .where(Ticket.created_by_user_id == current_user.id, Ticket.is_active == True)
        .order_by(Ticket.created_at.desc())
    )
    tickets = result.scalars().all()
    return success_response(data=[_ticket_dict(t) for t in tickets])


@router.post("/", summary="Create a support ticket")
async def create_ticket(
    payload: dict,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Generate ticket number
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d%H%M")
    ticket_number = f"TKT-{ts}-{str(uuid.uuid4())[:4].upper()}"

    ticket = Ticket(
        ticket_number=ticket_number,
        created_by_user_id=current_user.id,
        subject=payload.get("subject", ""),
        description=payload.get("description", ""),
        category=payload.get("category", "general"),
        priority=payload.get("priority", "medium"),
        status="open",
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    return success_response(
        data=_ticket_dict(ticket),
        message=f"Ticket {ticket.ticket_number} created successfully",
    )


@router.get("/all", summary="List all tickets (Admin/HR)")
async def list_all_tickets(
    current_user=Depends(require_roles(Roles.ADMIN_HR)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Ticket).where(Ticket.is_active == True).order_by(Ticket.created_at.desc())
    )
    tickets = result.scalars().all()
    return success_response(data=[_ticket_dict(t) for t in tickets])


@router.put("/{ticket_id}/status", summary="Update ticket status (Admin/HR)")
async def update_ticket_status(
    ticket_id: str,
    payload: dict,
    current_user=Depends(require_roles(Roles.ADMIN_HR)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Ticket", ticket_id)

    ticket.status = payload.get("status", ticket.status)
    if payload.get("resolution"):
        ticket.ai_resolution_suggestion = payload["resolution"]
    await db.commit()

    return success_response(data=_ticket_dict(ticket), message="Ticket updated")
