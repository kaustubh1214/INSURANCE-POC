"""Health Cards router — /api/v1/health-cards/*"""
import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import Roles, get_current_user, require_roles
from app.core.response import success_response
from app.database import get_db
from app.modules.employees.repository import EmployeeRepository
from app.modules.health_cards.models import HealthCard

router = APIRouter(prefix="/health-cards", tags=["Health Cards"])


@router.get("/my-card", summary="Get my health card")
async def get_my_health_card(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns the health card for the currently authenticated employee."""
    emp_repo = EmployeeRepository(db)
    emp = await emp_repo.get_by_user_id(current_user.id)
    if not emp:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Employee profile")

    result = await db.execute(
        select(HealthCard).where(
            HealthCard.employee_id == emp.id,
            HealthCard.is_active == True,
        )
    )
    card = result.scalar_one_or_none()
    if not card:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Health card not yet issued for this employee")

    return success_response(data={
        "id":               card.id,
        "card_number":      card.card_number,
        "insurer_name":     card.insurer_name,
        "plan_name":        card.plan_name,
        "network_type":     card.network_type,
        "valid_from":       str(card.valid_from),
        "valid_to":         str(card.valid_to),
        "sum_insured":      card.sum_insured,
        "tpa_name":         card.tpa_name,
        "tpa_helpline":     card.tpa_helpline,
        "tpa_email":        card.tpa_email,
        "emergency_contact":card.emergency_contact,
        "card_status":      card.card_status,
    })


@router.post("/generate", summary="Generate health card for an employee (Admin/HR)")
async def generate_health_card(
    employee_id: str,
    insurer_name: str,
    plan_name: str | None = None,
    sum_insured: str | None = None,
    tpa_name: str | None = None,
    tpa_helpline: str | None = None,
    validity_years: int = 1,
    current_user=Depends(require_roles(Roles.ADMIN_HR)),
    db: AsyncSession = Depends(get_db),
):
    """Issue or reissue a health card for an employee."""
    today = date.today()
    card_number = f"IBHC-{today.strftime('%Y')}-{str(uuid.uuid4())[:8].upper()}"

    card = HealthCard(
        employee_id=employee_id,
        card_number=card_number,
        insurer_name=insurer_name,
        plan_name=plan_name,
        valid_from=today,
        valid_to=today + timedelta(days=365 * validity_years),
        sum_insured=sum_insured,
        tpa_name=tpa_name,
        tpa_helpline=tpa_helpline,
        card_status="active",
    )
    db.add(card)
    await db.commit()
    await db.refresh(card)

    return success_response(
        data={"id": card.id, "card_number": card.card_number},
        message="Health card generated successfully",
    )
