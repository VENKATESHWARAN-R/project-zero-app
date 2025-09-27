from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class ReadinessStatus(str, Enum):
    READY = "ready"
    NOT_READY = "not_ready"


class DatabaseStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class HealthResponse(BaseModel):
    status: HealthStatus = Field(..., description="Overall service health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Health check timestamp")
    database: DatabaseStatus = Field(..., description="Database connection status")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ReadinessChecks(BaseModel):
    database: ReadinessStatus = Field(..., description="Database readiness status")
    auth_service: ReadinessStatus = Field(..., description="Auth service readiness status")


class ReadinessResponse(BaseModel):
    status: ReadinessStatus = Field(..., description="Overall service readiness status")
    service: str = Field(..., description="Service name")
    checks: ReadinessChecks = Field(..., description="Individual readiness checks")
    timestamp: datetime = Field(..., description="Readiness check timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }