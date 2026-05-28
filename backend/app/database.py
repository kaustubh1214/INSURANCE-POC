"""
Database engine, session factory, and base model.
Uses SQLAlchemy 2.x async engine.

To switch from SQLite to PostgreSQL:
  - Change DATABASE_URL in .env to postgresql+asyncpg://...
  - That's it — no code changes needed.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,          # Log SQL queries in debug mode
    future=True,
    # SQLite-specific: allow use across threads (needed for async)
    connect_args={"check_same_thread": False}
    if "sqlite" in settings.database_url
    else {},
)


# ---------------------------------------------------------------------------
# Session Factory
# ---------------------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,       # Don't expire objects after commit
    autocommit=False,
    autoflush=False,
)


# ---------------------------------------------------------------------------
# Base Declarative Model
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    """
    All SQLAlchemy models inherit from this base.
    Provides a common interface for metadata and migrations.
    """
    pass


# ---------------------------------------------------------------------------
# Dependency: DB Session
# ---------------------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session.

    Usage in router:
        @router.get("/")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# DB Initialization
# ---------------------------------------------------------------------------
async def init_db() -> None:
    """
    Creates all tables defined in SQLAlchemy models.
    Called on application startup.
    Import all models before calling this to ensure they're registered.
    """
    # Import all models so SQLAlchemy knows about them
    from app.modules.users.models import User  # noqa: F401
    from app.modules.employees.models import Employee  # noqa: F401
    from app.modules.family.models import FamilyMember  # noqa: F401
    from app.modules.policies.models import Policy, PolicyEnrollment  # noqa: F401
    from app.modules.claims.models import (  # noqa: F401
        Claim,
        ClaimDocument,
        ClaimStatusHistory,
    )
    from app.modules.health_cards.models import HealthCard  # noqa: F401
    from app.modules.health_checkups.models import (  # noqa: F401
        HealthCheckup,
        LabPartner,
    )
    from app.modules.tickets.models import Ticket  # noqa: F401
    from app.modules.notifications.models import Notification  # noqa: F401
    from app.models.audit import AuditLog, AIAuditLog  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
