from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import logging
from typing import Union

from ..schemas.error import ErrorResponse, ValidationErrorResponse, ValidationErrorDetail

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    correlation_id = getattr(request.state, 'correlation_id', None)

    # Log the exception
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )

    error_response = ErrorResponse(
        error=f"HTTP {exc.status_code}",
        message=exc.detail,
        timestamp=datetime.utcnow()
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode='json'),
        headers={"X-Correlation-ID": correlation_id} if correlation_id else {}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    correlation_id = getattr(request.state, 'correlation_id', None)

    # Extract validation errors
    validation_errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        validation_errors.append(
            ValidationErrorDetail(
                field=field_path,
                message=error["msg"],
                value=error.get("input")
            )
        )

    # Log the validation error
    logger.warning(
        f"Validation Error: {len(validation_errors)} field(s) failed validation",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "validation_errors": [error.model_dump() for error in validation_errors]
        }
    )

    error_response = ValidationErrorResponse(
        message=f"Validation failed for {len(validation_errors)} field(s)",
        validation_errors=validation_errors,
        timestamp=datetime.utcnow()
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(mode='json'),
        headers={"X-Correlation-ID": correlation_id} if correlation_id else {}
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors."""
    correlation_id = getattr(request.state, 'correlation_id', None)

    # Log the database error
    logger.error(
        f"Database Error: {type(exc).__name__}",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "error_type": type(exc).__name__,
            "error_message": str(exc)
        },
        exc_info=True
    )

    error_response = ErrorResponse(
        error="Database Error",
        message="A database error occurred while processing your request",
        details={"error_type": type(exc).__name__},
        timestamp=datetime.utcnow()
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(mode='json'),
        headers={"X-Correlation-ID": correlation_id} if correlation_id else {}
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions."""
    correlation_id = getattr(request.state, 'correlation_id', None)

    # Log the unexpected error
    logger.error(
        f"Unexpected Error: {type(exc).__name__}",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "error_type": type(exc).__name__,
            "error_message": str(exc)
        },
        exc_info=True
    )

    error_response = ErrorResponse(
        error="Internal Server Error",
        message="An unexpected error occurred while processing your request",
        details={
            "error_type": type(exc).__name__,
            "correlation_id": correlation_id
        },
        timestamp=datetime.utcnow()
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(mode='json'),
        headers={"X-Correlation-ID": correlation_id} if correlation_id else {}
    )


def setup_exception_handlers(app):
    """Setup all exception handlers for the FastAPI app."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)