"""Health check endpoints."""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from src.database import check_database_connection
from src.schemas import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Basic health check endpoint",
)
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(UTC),
    )


@router.get(
    "/health/ready",
    response_model=HealthResponse,
    summary="Readiness check",
    description="Readiness check including database connectivity",
)
async def readiness_check():
    """Readiness check including database connectivity."""
    timestamp = datetime.now(UTC)

    # Check database connection
    try:
        db_connected = check_database_connection()

        if db_connected:
            return HealthResponse(
                status="ready",
                timestamp=timestamp,
                database="connected",
            )
        # Service not ready due to database issues
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        )

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready",
        )
