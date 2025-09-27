from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from ..database import get_db
from ..schemas.health import HealthResponse, ReadinessResponse, ReadinessChecks, HealthStatus, ReadinessStatus, DatabaseStatus
from ..services.auth_service import AuthService
from ..config import get_auth_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Basic health check endpoint."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        database_status = DatabaseStatus.CONNECTED
        overall_status = HealthStatus.HEALTHY
    except Exception:
        database_status = DatabaseStatus.DISCONNECTED
        overall_status = HealthStatus.UNHEALTHY

    return HealthResponse(
        status=overall_status,
        service="user-profile-service",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        database=database_status
    )


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness_check(
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Readiness check with dependency verification."""
    checks = ReadinessChecks(
        database=ReadinessStatus.NOT_READY,
        auth_service=ReadinessStatus.NOT_READY
    )

    # Check database
    try:
        db.execute(text("SELECT 1"))
        checks.database = ReadinessStatus.READY
    except Exception:
        pass

    # Check auth service
    try:
        auth_healthy = await auth_service.check_auth_service_health()
        if auth_healthy:
            checks.auth_service = ReadinessStatus.READY
    except Exception:
        pass

    # Overall readiness
    overall_status = ReadinessStatus.READY if (
        checks.database == ReadinessStatus.READY and
        checks.auth_service == ReadinessStatus.READY
    ) else ReadinessStatus.NOT_READY

    return ReadinessResponse(
        status=overall_status,
        service="user-profile-service",
        checks=checks,
        timestamp=datetime.utcnow()
    )