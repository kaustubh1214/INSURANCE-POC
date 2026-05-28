"""
InsureBridge — FastAPI Application Entry Point
Registers all routers, middleware, exception handlers, and startup events.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import AppException
from app.core.response import error_response
from app.database import init_db

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# App Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: Initialize database tables.
    Shutdown: Close connections (SQLAlchemy handles this automatically).
    """
    logger.info("🚀 InsureBridge starting up...")
    await init_db()
    logger.info("✅ Database initialized")

    # Seed admin user + employee profile on first run
    await seed_admin()

    # Seed sample insurance policies on first run
    await seed_policies()

    # Seed lab partners for health checkup booking
    await seed_lab_partners()

    yield

    logger.info("👋 InsureBridge shutting down")


async def seed_admin():
    """Create the default admin user + employee profile if they don't exist."""
    from datetime import date
    from app.database import AsyncSessionLocal
    from app.modules.users.repository import UserRepository
    from app.modules.employees.repository import EmployeeRepository
    from app.core.security import hash_password

    async with AsyncSessionLocal() as db:
        user_repo = UserRepository(db)
        emp_repo = EmployeeRepository(db)

        # --- Seed admin user ---
        user = await user_repo.get_by_email(settings.admin_email)
        if not user:
            user = await user_repo.create(
                email=settings.admin_email,
                hashed_password=hash_password(settings.admin_password),
                full_name=settings.admin_name,
                role="admin",
                is_verified=True,
            )
            await db.flush()
            logger.info(f"✅ Admin user seeded: {settings.admin_email}")

        # --- Seed employee profile for admin (needed for family, claims, health card) ---
        existing_emp = await emp_repo.get_by_user_id(user.id)
        if not existing_emp:
            await emp_repo.create(
                user_id=user.id,
                employee_code="EMP-ADMIN-001",
                department="Administration",
                designation="System Administrator",
                employment_status="active",
                company_name="InsureBridge Corp",
                date_of_joining=date(2024, 1, 1),
                city="Mumbai",
                state="Maharashtra",
            )
            logger.info("✅ Admin employee profile seeded")

        await db.commit()


async def seed_policies():
    """Seed sample insurance policies if none exist."""
    from datetime import date
    from app.database import AsyncSessionLocal
    from app.modules.policies.models import Policy
    from sqlalchemy import select, func

    async with AsyncSessionLocal() as db:
        count = await db.execute(select(func.count()).select_from(Policy))
        if count.scalar() > 0:
            return  # already seeded

        sample_policies = [
            Policy(
                policy_number="POL-HEALTH-001",
                policy_name="Star Family Floater — Gold",
                policy_type="health",
                insurer_name="Star Health Insurance",
                premium_amount=18500,
                sum_insured=500000,
                premium_frequency="annual",
                policy_start_date=date(2024, 4, 1),
                policy_end_date=date(2025, 3, 31),
                description="Comprehensive family floater health insurance covering hospitalization, day-care, and pre/post hospitalization expenses.",
                benefits_summary="Hospitalization | Day-care procedures | Pre & post hospitalization (60/90 days) | Ambulance cover ₹2,000 | Annual health check-up | No-claim bonus 10% p.a.",
                exclusions="Pre-existing diseases (2-year waiting) | Cosmetic surgery | Self-inflicted injuries | War/nuclear perils",
                max_family_members=6,
                is_corporate=True,
            ),
            Policy(
                policy_number="POL-HEALTH-002",
                policy_name="HDFC ERGO — Individual Shield",
                policy_type="health",
                insurer_name="HDFC ERGO General Insurance",
                premium_amount=9200,
                sum_insured=300000,
                premium_frequency="annual",
                policy_start_date=date(2024, 4, 1),
                policy_end_date=date(2025, 3, 31),
                description="Individual health plan with room rent waiver and OPD cover.",
                benefits_summary="Hospitalization | OPD cover ₹5,000 | Room rent waiver | Mental health cover | AYUSH treatment",
                exclusions="Pre-existing diseases (3-year waiting) | Dental (unless accidental) | Obesity treatment",
                max_family_members=1,
                is_corporate=True,
            ),
            Policy(
                policy_number="POL-HEALTH-003",
                policy_name="Bajaj Allianz — Super Family Floater",
                policy_type="health",
                insurer_name="Bajaj Allianz General Insurance",
                premium_amount=24000,
                sum_insured=1000000,
                premium_frequency="annual",
                policy_start_date=date(2024, 4, 1),
                policy_end_date=date(2025, 3, 31),
                description="Super-top-up plan with ₹10L sum insured. Ideal for senior employees and large families.",
                benefits_summary="Hospitalization | Critical illness rider | Maternity benefit ₹50,000 | New-born cover | Restoration benefit 100%",
                exclusions="Pre-existing (4-year waiting) | HIV/AIDS | Adventure sports",
                max_family_members=8,
                is_corporate=True,
            ),
            Policy(
                policy_number="POL-LIFE-001",
                policy_name="LIC Group Term Life — Corporate",
                policy_type="life",
                insurer_name="Life Insurance Corporation of India",
                premium_amount=4800,
                sum_insured=2500000,
                premium_frequency="annual",
                policy_start_date=date(2024, 4, 1),
                policy_end_date=date(2025, 3, 31),
                description="Group term life insurance providing life cover to all employees. Nominee receives sum insured on death of employee.",
                benefits_summary="Life cover ₹25L | Accidental death benefit 2x | Total/permanent disability | Terminal illness cover",
                exclusions="Suicide (1st year) | Aviation risk | War/terrorism",
                max_family_members=1,
                is_corporate=True,
            ),
            Policy(
                policy_number="POL-ACC-001",
                policy_name="New India — Group Personal Accident",
                policy_type="accidental",
                insurer_name="New India Assurance",
                premium_amount=2100,
                sum_insured=1000000,
                premium_frequency="annual",
                policy_start_date=date(2024, 4, 1),
                policy_end_date=date(2025, 3, 31),
                description="Personal accident cover for all employees including on-duty and off-duty accidents.",
                benefits_summary="Accidental death ₹10L | Permanent total disability ₹10L | Permanent partial disability (% of SI) | Temporary total disability ₹5,000/week (max 52 weeks) | Medical reimbursement ₹1L",
                exclusions="Intoxication | Self-inflicted | War | Pre-existing disability",
                max_family_members=1,
                is_corporate=True,
            ),
        ]

        for policy in sample_policies:
            db.add(policy)

        await db.commit()
        logger.info(f"✅ {len(sample_policies)} sample policies seeded")


async def seed_lab_partners():
    """Seed sample lab partners for health checkup booking."""
    from app.database import AsyncSessionLocal
    from app.modules.health_checkups.models import LabPartner
    from sqlalchemy import select, func

    async with AsyncSessionLocal() as db:
        count = await db.execute(select(func.count()).select_from(LabPartner))
        if count.scalar() > 0:
            return  # already seeded

        labs = [
            LabPartner(
                name="Dr. Lal PathLabs",
                code="LAB-LPL-001",
                city="Mumbai",
                state="Maharashtra",
                address="15, Linking Road, Bandra West",
                phone="022-4060-2020",
                email="mumbai@lalpathlabs.com",
                is_home_collection=True,
                rating=4.8,
            ),
            LabPartner(
                name="SRL Diagnostics",
                code="LAB-SRL-001",
                city="Mumbai",
                state="Maharashtra",
                address="SRL House, Andheri East",
                phone="022-6799-8000",
                email="andheri@srlworld.com",
                is_home_collection=True,
                rating=4.6,
            ),
            LabPartner(
                name="Metropolis Healthcare",
                code="LAB-MET-001",
                city="Bangalore",
                state="Karnataka",
                address="No. 12, Koramangala 4th Block",
                phone="080-6740-0000",
                email="bangalore@metropolisindia.com",
                is_home_collection=True,
                rating=4.7,
            ),
            LabPartner(
                name="Thyrocare Technologies",
                code="LAB-THY-001",
                city="Navi Mumbai",
                state="Maharashtra",
                address="D-37/1, TTC Industrial Area, Turbhe",
                phone="1800-103-3838",
                email="support@thyrocare.com",
                is_home_collection=True,
                rating=4.5,
            ),
            LabPartner(
                name="Apollo Diagnostics",
                code="LAB-APL-001",
                city="Hyderabad",
                state="Telangana",
                address="Apollo Health City, Jubilee Hills",
                phone="040-2360-7777",
                email="hyderabad@apollodiagnostics.in",
                is_home_collection=False,
                rating=4.9,
            ),
        ]

        for lab in labs:
            db.add(lab)

        await db.commit()
        logger.info(f"✅ {len(labs)} lab partners seeded")


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## InsureBridge — Enterprise Insurance & Employee Benefits Platform

**Key features:**
- JWT authentication with RBAC (5 roles)
- Employee benefit portal APIs
- Multi-policy management
- AI-powered claims workflow
- OCR document processing
- Health checkup scheduling
- Audit trail on all operations
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=str(exc.detail),
            error_code=getattr(exc, "error_code", "APP_ERROR"),
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with a clean response."""
    errors = []
    for error in exc.errors():
        field = " → ".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            message=f"Validation failed: {'; '.join(errors)}",
            error_code="VALIDATION_ERROR",
        ),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected errors — never expose internals."""
    logger.exception(f"Unhandled exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            message="An unexpected error occurred. Please try again.",
            error_code="INTERNAL_ERROR",
        ),
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.employees.router import router as employees_router
from app.modules.family.router import router as family_router
from app.modules.policies.router import router as policies_router
from app.modules.claims.router import router as claims_router
from app.modules.health_cards.router import router as health_cards_router
from app.modules.health_checkups.router import router as health_checkups_router
from app.modules.tickets.router import router as tickets_router

PREFIX = settings.api_v1_prefix

app.include_router(auth_router, prefix=PREFIX)
app.include_router(users_router, prefix=PREFIX)
app.include_router(employees_router, prefix=PREFIX)
app.include_router(family_router, prefix=PREFIX)
app.include_router(policies_router, prefix=PREFIX)
app.include_router(claims_router, prefix=PREFIX)
app.include_router(health_cards_router, prefix=PREFIX)
app.include_router(health_checkups_router, prefix=PREFIX)
app.include_router(tickets_router, prefix=PREFIX)


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"])
async def health_check():
    """System health check — used by Docker and load balancers."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": f"Welcome to {settings.app_name} API",
        "docs": "/docs",
        "version": settings.app_version,
    }
