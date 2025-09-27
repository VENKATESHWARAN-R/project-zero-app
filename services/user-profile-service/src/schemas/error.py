from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type or category")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(..., description="Error timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ValidationErrorDetail(BaseModel):
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    value: Optional[Any] = Field(None, description="Invalid value provided")


class ValidationErrorResponse(ErrorResponse):
    error: str = Field("Validation failed", description="Error type")
    validation_errors: Optional[list[ValidationErrorDetail]] = Field(None, description="Detailed validation errors")


class AuthenticationErrorResponse(ErrorResponse):
    error: str = Field("Unauthorized", description="Error type")
    message: str = Field("Invalid or missing authentication token", description="Authentication error message")


class AuthorizationErrorResponse(ErrorResponse):
    error: str = Field("Forbidden", description="Error type")
    message: str = Field("Insufficient permissions for this operation", description="Authorization error message")


class NotFoundErrorResponse(ErrorResponse):
    error: str = Field("Not Found", description="Error type")
    resource_type: Optional[str] = Field(None, description="Type of resource not found")
    resource_id: Optional[str] = Field(None, description="ID of resource not found")


class ConflictErrorResponse(ErrorResponse):
    error: str = Field("Conflict", description="Error type")
    conflict_type: Optional[str] = Field(None, description="Type of conflict")


class InternalServerErrorResponse(ErrorResponse):
    error: str = Field("Internal Server Error", description="Error type")
    message: str = Field("An unexpected error occurred", description="Generic error message")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID for debugging")