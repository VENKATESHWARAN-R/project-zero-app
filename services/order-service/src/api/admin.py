"""
Admin order management API endpoints.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..clients.auth_client import AuthClient, AuthorizationError
from ..services.order_service import OrderService
from ..schemas.orders import AdminOrderHistoryResponse, AdminOrderResponse, UpdateStatusRequest, OrderResponse
from ..schemas.common import OrderStatus
from ..utils.validation import (
    create_unauthorized_error,
    create_forbidden_error,
    validate_pagination_params,
    validate_order_id,
    handle_service_error
)
from ..logging_config import get_logger, set_correlation_id

logger = get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


async def get_admin_user(
    authorization: str = Header(..., description="Bearer JWT token"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Dependency to get current admin user."""
    if not authorization.startswith("Bearer "):
        raise create_unauthorized_error("Invalid authorization header format")

    token = authorization[7:]

    try:
        auth_client = AuthClient()
        user_data = await auth_client.verify_token(token)

        # Check admin privileges
        auth_client.require_admin_role(user_data)

        return user_data
    except AuthorizationError as e:
        logger.warning("Admin access denied", extra={"error": str(e)})
        raise create_forbidden_error("Admin privileges required")


@router.get(
    "/orders",
    response_model=AdminOrderHistoryResponse,
    summary="Get all orders (admin)",
    description="Retrieve orders across all users with admin privileges"
)
async def get_all_orders_admin(
    status_filter: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of orders"),
    offset: int = Query(0, ge=0, description="Number of orders to skip"),
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get all orders for admin management."""
    if x_correlation_id:
        set_correlation_id(x_correlation_id)

    validate_pagination_params(limit, offset)

    try:
        # TODO: Implement admin order retrieval with cross-user access
        # This would be similar to get_user_orders but without user_id restriction

        logger.info("Admin order retrieval", extra={
            "admin_user_id": admin_user["user_id"],
            "status_filter": status_filter.value if status_filter else None,
            "user_filter": user_id
        })

        # Placeholder response
        return AdminOrderHistoryResponse(
            orders=[],
            total=0,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        logger.error("Error retrieving admin orders", extra={
            "error": str(e),
            "admin_user_id": admin_user["user_id"]
        })
        raise handle_service_error(e, "order_service")


@router.put(
    "/orders/{order_id}/status",
    response_model=OrderResponse,
    summary="Update order status (admin)",
    description="Update order status for fulfillment tracking"
)
async def update_order_status_admin(
    order_id: int,
    request: UpdateStatusRequest,
    admin_user: Dict[str, Any] = Depends(get_admin_user),
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Update order status with admin privileges."""
    if x_correlation_id:
        set_correlation_id(x_correlation_id)

    validate_order_id(order_id)

    try:
        order_service = OrderService(db)

        updated_order = await order_service.update_order_status(
            order_id=order_id,
            new_status=request.status,
            user_data=admin_user,
            notes=request.notes
        )

        logger.info("Admin order status update", extra={
            "order_id": order_id,
            "new_status": request.status.value,
            "admin_user_id": admin_user["user_id"]
        })

        return OrderResponse(
            id=updated_order.id,
            order_number=updated_order.order_number,
            user_id=updated_order.user_id,
            status=OrderStatus(updated_order.status.value),
            subtotal=float(updated_order.subtotal),
            tax_rate=float(updated_order.tax_rate),
            tax_amount=float(updated_order.tax_amount),
            shipping_cost=float(updated_order.shipping_cost),
            total=float(updated_order.total),
            currency=updated_order.currency,
            created_at=updated_order.created_at,
            updated_at=updated_order.updated_at,
            modification_count=updated_order.modification_count
        )

    except Exception as e:
        logger.error("Error updating order status", extra={
            "error": str(e),
            "order_id": order_id,
            "admin_user_id": admin_user["user_id"]
        })
        raise handle_service_error(e, "order_service")