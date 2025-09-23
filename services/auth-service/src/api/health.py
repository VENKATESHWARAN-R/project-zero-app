"""
Health check API endpoint.
Implements GET /health for service monitoring.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.database import check_database_connection
from src.schemas.auth import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns service health status and database connectivity.
    """
    try:
        # Check database connection
        db_connected = check_database_connection()
        db_status = "connected" if db_connected else "disconnected"

        # Determine overall health status
        is_healthy = db_connected
        overall_status = "healthy" if is_healthy else "unhealthy"

        # Create response
        health_data = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_status
        }

        # Return appropriate status code
        status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

        return JSONResponse(
            status_code=status_code,
            content=health_data
        )

    except Exception as e:
        logger.error(f"Error during health check: {e}")

        # Return unhealthy status on any error
        health_data = {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "error"
        }

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_data
        )