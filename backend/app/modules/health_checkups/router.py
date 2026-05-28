"""Health Checkups router — /api/v1/health-checkups/*"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import get_current_user
from app.core.response import success_response
from app.database import get_db
from app.modules.employees.repository import EmployeeRepository
from app.modules.health_checkups.models import HealthCheckup, LabPartner

router = APIRouter(prefix="/health-checkups", tags=["Health Checkups"])


@router.get("/labs", summary="List partner labs")
async def list_labs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LabPartner).where(LabPartner.is_active == True))
    labs = result.scalars().all()
    return success_response(data=[{
        "id":                 l.id,
        "name":               l.name,
        "city":               l.city,
        "state":              l.state,
        "phone":              l.phone,
        "is_home_collection": l.is_home_collection,
        "rating":             l.rating,
    } for l in labs])


@router.get("/", summary="List my health checkups")
async def list_my_checkups(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    emp_repo = EmployeeRepository(db)
    emp = await emp_repo.get_by_user_id(current_user.id)
    if not emp:
        return success_response(data=[])

    result = await db.execute(
        select(HealthCheckup)
        .where(HealthCheckup.employee_id == emp.id, HealthCheckup.is_active == True)
        .order_by(HealthCheckup.created_at.desc())
    )
    checkups = result.scalars().all()
    return success_response(data=[{
        "id":                    c.id,
        "checkup_type":          c.checkup_type,
        "package_name":          c.package_name,
        "scheduled_date":        str(c.scheduled_date) if c.scheduled_date else None,
        "preferred_date":        str(c.preferred_date) if c.preferred_date else None,
        "status":                c.status,
        "is_home_collection":    c.is_home_collection,
        "report_url":            c.report_url,
        "ai_health_summary":     c.ai_health_summary,
        "follow_up_recommended": c.follow_up_recommended,
        "created_at":            c.created_at.isoformat(),
    } for c in checkups])


@router.post("/", summary="Book a health checkup")
async def book_checkup(
    payload: dict,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from datetime import date as _date
    emp_repo = EmployeeRepository(db)
    emp = await emp_repo.get_by_user_id(current_user.id)
    if not emp:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Employee profile")

    preferred = payload.get("preferred_date")
    checkup = HealthCheckup(
        employee_id=emp.id,
        checkup_type=payload.get("checkup_type", "annual_health_checkup"),
        package_name=payload.get("package_name"),
        lab_partner_id=payload.get("lab_partner_id"),
        preferred_date=_date.fromisoformat(preferred) if preferred else None,
        is_home_collection=payload.get("is_home_collection", False),
        status="booked",
    )
    db.add(checkup)
    await db.commit()
    await db.refresh(checkup)

    return success_response(
        data={"id": checkup.id, "status": checkup.status},
        message="Health checkup booked successfully",
    )
