"""
Input validation and error handling utilities.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from pydantic import ValidationError

from ..logging_config import get_logger
from ..schemas.common import ErrorResponse

logger = get_logger(__name__)


def create_error_response(
    error_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> HTTPException:
    """
    Create a standardized HTTP exception with error response.

    Args:
        error_type: Type of error
        message: Human-readable error message
        details: Optional additional error details
        status_code: HTTP status code

    Returns:
        HTTPException with structured error response
    """
    error_response = ErrorResponse(
        error=error_type,
        message=message,
        details=details,
        timestamp=datetime.utcnow()
    )

    logger.warning("API error response created", extra={
        "error_type": error_type,
        "message": message,
        "status_code": status_code,
        "details": details
    })

    raise HTTPException(
        status_code=status_code,
        detail=error_response.model_dump()
    )


def create_validation_error(validation_error: ValidationError) -> HTTPException:
    """
    Create HTTP exception from Pydantic validation error.

    Args:
        validation_error: Pydantic ValidationError

    Returns:
        HTTPException with validation error details
    """
    error_details = []
    for error in validation_error.errors():
        error_details.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return create_error_response(
        error_type="validation_error",
        message="Request validation failed",
        details={"validation_errors": error_details},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


def validate_pagination_params(limit: int, offset: int, max_limit: int = 100) -> None:
    """
    Validate pagination parameters.

    Args:
        limit: Number of items to return
        offset: Number of items to skip
        max_limit: Maximum allowed limit

    Raises:
        HTTPException: If parameters are invalid
    """
    if limit < 1:
        create_error_response(
            "invalid_parameter",
            "Limit must be positive",
            {"parameter": "limit", "value": limit}
        )

    if limit > max_limit:
        create_error_response(
            "invalid_parameter",
            f"Limit cannot exceed {max_limit}",
            {"parameter": "limit", "value": limit, "max_limit": max_limit}
        )

    if offset < 0:
        create_error_response(
            "invalid_parameter",
            "Offset cannot be negative",
            {"parameter": "offset", "value": offset}
        )


def validate_order_id(order_id: int) -> None:
    """
    Validate order ID parameter.

    Args:
        order_id: Order ID to validate

    Raises:
        HTTPException: If order ID is invalid
    """
    if order_id <= 0:
        create_error_response(
            "invalid_parameter",
            "Order ID must be positive",
            {"parameter": "order_id", "value": order_id},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


def handle_service_error(error: Exception, service_name: str) -> HTTPException:
    """
    Handle service-specific errors and convert to HTTP exceptions.

    Args:
        error: Exception from service
        service_name: Name of the service that failed

    Returns:
        HTTPException with appropriate status code
    """
    error_str = str(error)

    # Authentication/Authorization errors
    if "authentication" in error_str.lower() or "unauthorized" in error_str.lower():
        return create_error_response(
            "authentication_error",
            "Authentication failed",
            {"service": service_name, "error": error_str},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    if "authorization" in error_str.lower() or "forbidden" in error_str.lower():
        return create_error_response(
            "authorization_error",
            "Access denied",
            {"service": service_name, "error": error_str},
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Business logic errors
    if "empty" in error_str.lower() and "cart" in error_str.lower():
        return create_error_response(
            "empty_cart",
            "Cart is empty - cannot create order",
            {"service": service_name},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    if "unavailable" in error_str.lower():
        return create_error_response(
            "product_unavailable",
            "One or more products are unavailable",
            {"service": service_name, "error": error_str},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    if "insufficient" in error_str.lower() or "stock" in error_str.lower():
        return create_error_response(
            "insufficient_stock",
            "Insufficient stock for one or more items",
            {"service": service_name, "error": error_str},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    # Service availability errors
    if "unavailable" in service_name.lower() or "timeout" in error_str.lower():
        return create_error_response(
            "service_unavailable",
            f"{service_name} is currently unavailable",
            {"service": service_name, "error": error_str},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    # Default to internal server error
    logger.error(f"Unhandled service error from {service_name}", extra={
        "service": service_name,
        "error": error_str,
        "error_type": type(error).__name__
    })

    return create_error_response(
        "internal_error",
        "An internal error occurred",
        {"service": service_name},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def create_not_found_error(resource_type: str, resource_id: Any) -> HTTPException:
    """
    Create a 404 not found error.

    Args:
        resource_type: Type of resource (e.g., "order", "user")
        resource_id: ID of the resource

    Returns:
        HTTPException with 404 status
    """
    return create_error_response(
        "not_found",
        f"{resource_type.title()} not found",
        {"resource_type": resource_type, "resource_id": resource_id},
        status_code=status.HTTP_404_NOT_FOUND
    )


def create_forbidden_error(message: str = "Access denied") -> HTTPException:
    """
    Create a 403 forbidden error.

    Args:
        message: Custom error message

    Returns:
        HTTPException with 403 status
    """
    return create_error_response(
        "forbidden",
        message,
        status_code=status.HTTP_403_FORBIDDEN
    )


def create_unauthorized_error(message: str = "Authentication required") -> HTTPException:
    """
    Create a 401 unauthorized error.

    Args:
        message: Custom error message

    Returns:
        HTTPException with 401 status
    """
    return create_error_response(
        "unauthorized",
        message,
        status_code=status.HTTP_401_UNAUTHORIZED
    )