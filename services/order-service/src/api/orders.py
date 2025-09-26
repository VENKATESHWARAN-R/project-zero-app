"""
Order management API endpoints.

Handles order creation, retrieval, modification, and cancellation.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..clients.auth_client import AuthClient, AuthenticationError, AuthorizationError
from ..services.order_service import OrderService, OrderServiceError, InvalidOrderStateError, InsufficientPermissionsError
from ..schemas.orders import (
    CreateOrderRequest,
    ModifyOrderRequest,
    UpdateStatusRequest,
    OrderResponse,
    OrderDetailResponse,
    OrderHistoryResponse,
    OrderStatusHistoryResponse,
)
from ..schemas.common import OrderStatus
from ..utils.validation import (
    create_error_response,
    create_not_found_error,
    create_forbidden_error,
    create_unauthorized_error,
    validate_pagination_params,
    validate_order_id,
    handle_service_error
)
from ..logging_config import get_logger, set_correlation_id

logger = get_logger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])


async def get_current_user(
    authorization: str = Header(..., description="Bearer JWT token"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Dependency to get current authenticated user."""
    if not authorization.startswith("Bearer "):
        raise create_unauthorized_error("Invalid authorization header format")

    token = authorization[7:]  # Remove "Bearer " prefix

    try:
        auth_client = AuthClient()
        user_data = await auth_client.verify_token(token)
        return user_data
    except AuthenticationError as e:
        logger.warning("Authentication failed", extra={"error": str(e)})
        raise create_unauthorized_error(str(e))


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new order from cart",
    description="Convert cart items to order, calculate totals, and create order record"
)
async def create_order(
    request: CreateOrderRequest,
    user_data: Dict[str, Any] = Depends(get_current_user),
    authorization: str = Header(...),
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Create a new order from the user's cart."""
    # Set correlation ID for request tracing
    if x_correlation_id:
        set_correlation_id(x_correlation_id)

    auth_token = authorization[7:]  # Remove "Bearer " prefix

    try:
        order_service = OrderService(db)

        order = await order_service.create_order(
            user_data=user_data,
            shipping_address_data=request.shipping_address.model_dump(),
            auth_token=auth_token,
            notes=request.notes
        )

        logger.info("Order created via API", extra={
            "order_id": order.id,
            "user_id": user_data["user_id"],
            "total": float(order.total)
        })

        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            user_id=order.user_id,
            status=OrderStatus(order.status.value),
            subtotal=float(order.subtotal),
            tax_rate=float(order.tax_rate),
            tax_amount=float(order.tax_amount),
            shipping_cost=float(order.shipping_cost),
            total=float(order.total),
            currency=order.currency,
            created_at=order.created_at,
            updated_at=order.updated_at,
            modification_count=order.modification_count
        )

    except OrderServiceError as e:
        raise handle_service_error(e, "order_service")
    except Exception as e:
        logger.error("Unexpected error during order creation", extra={
            "error": str(e),
            "user_id": user_data["user_id"]
        })
        raise create_error_response(
            "internal_error",
            "An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get(
    "/",
    response_model=OrderHistoryResponse,
    summary="Get user order history",
    description="Retrieve all orders for authenticated user with pagination and filtering"
)
async def get_order_history(
    status_filter: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip"),
    user_data: Dict[str, Any] = Depends(get_current_user),
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get order history for the authenticated user."""
    if x_correlation_id:
        set_correlation_id(x_correlation_id)

    validate_pagination_params(limit, offset)

    try:
        order_service = OrderService(db)
        orders, total_count = order_service.get_user_orders(
            user_id=user_data["user_id"],
            status_filter=status_filter,
            limit=limit,
            offset=offset
        )

        order_responses = [
            OrderResponse(
                id=order.id,
                order_number=order.order_number,
                user_id=order.user_id,
                status=OrderStatus(order.status.value),
                subtotal=float(order.subtotal),
                tax_rate=float(order.tax_rate),
                tax_amount=float(order.tax_amount),
                shipping_cost=float(order.shipping_cost),
                total=float(order.total),
                currency=order.currency,
                created_at=order.created_at,
                updated_at=order.updated_at,
                modification_count=order.modification_count
            )
            for order in orders
        ]

        logger.info("Order history retrieved", extra={
            "user_id": user_data["user_id"],
            "count": len(orders),
            "total": total_count
        })

        return OrderHistoryResponse(
            orders=order_responses,
            total=total_count,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        logger.error("Error retrieving order history", extra={
            "error": str(e),
            "user_id": user_data["user_id"]
        })
        raise handle_service_error(e, "order_service")


@router.get(
    "/{order_id}",
    response_model=OrderDetailResponse,
    summary="Get order details",
    description="Retrieve complete order information including items and shipping address"
)
async def get_order_details(
    order_id: int,
    user_data: Dict[str, Any] = Depends(get_current_user),
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get detailed information for a specific order."""
    if x_correlation_id:
        set_correlation_id(x_correlation_id)

    validate_order_id(order_id)

    try:
        order_service = OrderService(db)
        order = order_service.get_order_by_id(order_id, user_data)

        if not order:
            raise create_not_found_error("order", order_id)

        # Convert order items to response format
        order_items = [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "product_sku": item.product_sku,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "total_price": float(item.total_price),
                "weight": float(item.weight)
            }
            for item in order.items
        ]

        # Convert shipping address to response format
        shipping_address = {
            "id": order.shipping_address.id,
            "recipient_name": order.shipping_address.recipient_name,
            "company": order.shipping_address.company,
            "address_line_1": order.shipping_address.address_line_1,
            "address_line_2": order.shipping_address.address_line_2,
            "city": order.shipping_address.city,
            "state_province": order.shipping_address.state_province,
            "postal_code": order.shipping_address.postal_code,
            "country": order.shipping_address.country,
            "phone": order.shipping_address.phone,
            "delivery_instructions": order.shipping_address.delivery_instructions
        }

        logger.info("Order details retrieved", extra={
            "order_id": order_id,
            "user_id": user_data["user_id"]
        })

        return OrderDetailResponse(
            id=order.id,
            order_number=order.order_number,
            user_id=order.user_id,
            status=OrderStatus(order.status.value),
            subtotal=float(order.subtotal),
            tax_rate=float(order.tax_rate),
            tax_amount=float(order.tax_amount),
            shipping_cost=float(order.shipping_cost),
            total=float(order.total),
            currency=order.currency,
            created_at=order.created_at,
            updated_at=order.updated_at,
            modification_count=order.modification_count,
            items=order_items,
            shipping_address=shipping_address
        )

    except InsufficientPermissionsError:
        raise create_forbidden_error("Access denied - not order owner")
    except Exception as e:
        logger.error("Error retrieving order details", extra={
            "error": str(e),
            "order_id": order_id,
            "user_id": user_data["user_id"]
        })
        raise handle_service_error(e, "order_service")


@router.patch(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Modify order",
    description="Update order details (status-dependent restrictions apply)"
)
async def modify_order(
    order_id: int,
    request: ModifyOrderRequest,
    user_data: Dict[str, Any] = Depends(get_current_user),
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Modify an existing order."""
    if x_correlation_id:
        set_correlation_id(x_correlation_id)

    validate_order_id(order_id)

    # TODO: Implement order modification logic
    # This would include validation of what can be modified based on order status
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Order modification not yet implemented"
    )


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    summary="Cancel order",
    description="Cancel order if status allows cancellation"
)
async def cancel_order(
    order_id: int,
    reason: Optional[str] = None,
    user_data: Dict[str, Any] = Depends(get_current_user),
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Cancel an order."""
    if x_correlation_id:
        set_correlation_id(x_correlation_id)

    validate_order_id(order_id)

    try:
        order_service = OrderService(db)
        order = order_service.get_order_by_id(order_id, user_data)

        if not order:
            raise create_not_found_error("order", order_id)

        if not order.is_cancellable:
            raise create_error_response(
                "invalid_operation",
                f"Order cannot be cancelled in {order.status.value} status",
                {"order_id": order_id, "current_status": order.status.value},
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        # Import model's OrderStatus to avoid confusion
        from ..models import OrderStatus as ModelOrderStatus

        # Update order status to cancelled
        updated_order = await order_service.update_order_status(
            order_id=order_id,
            new_status=ModelOrderStatus.CANCELLED,
            user_data=user_data,
            notes=reason
        )

        logger.info("Order cancelled", extra={
            "order_id": order_id,
            "user_id": user_data["user_id"],
            "reason": reason
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

    except (InsufficientPermissionsError, AuthorizationError):
        raise create_forbidden_error("Access denied - not order owner")
    except InvalidOrderStateError as e:
        raise create_error_response(
            "invalid_state",
            str(e),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        logger.error("Error cancelling order", extra={
            "error": str(e),
            "order_id": order_id,
            "user_id": user_data["user_id"]
        })
        raise handle_service_error(e, "order_service")


@router.put(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Update order status",
    description="Update order status (admin privileges required)"
)
async def update_order_status(
    order_id: int,
    request: UpdateStatusRequest,
    user_data: Dict[str, Any] = Depends(get_current_user),
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Update order status (admin only)."""
    if x_correlation_id:
        set_correlation_id(x_correlation_id)

    validate_order_id(order_id)

    try:
        order_service = OrderService(db)

        updated_order = await order_service.update_order_status(
            order_id=order_id,
            new_status=request.status,
            user_data=user_data,
            notes=request.notes
        )

        logger.info("Order status updated via API", extra={
            "order_id": order_id,
            "new_status": request.status.value,
            "updated_by": user_data["user_id"]
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

    except (InsufficientPermissionsError, AuthorizationError):
        raise create_forbidden_error("Admin privileges required")
    except InvalidOrderStateError as e:
        raise create_error_response(
            "invalid_transition",
            str(e),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        logger.error("Error updating order status", extra={
            "error": str(e),
            "order_id": order_id,
            "user_id": user_data["user_id"]
        })
        raise handle_service_error(e, "order_service")


@router.get(
    "/{order_id}/status-history",
    response_model=OrderStatusHistoryResponse,
    summary="Get order status history",
    description="Retrieve complete status change history for an order"
)
async def get_order_status_history(
    order_id: int,
    user_data: Dict[str, Any] = Depends(get_current_user),
    x_correlation_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get status change history for an order."""
    if x_correlation_id:
        set_correlation_id(x_correlation_id)

    validate_order_id(order_id)

    # TODO: Implement status history retrieval
    # This would query the OrderModification table for status changes
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Status history retrieval not yet implemented"
    )