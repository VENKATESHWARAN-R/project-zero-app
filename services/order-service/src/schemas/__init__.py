"""
Pydantic schemas for request/response validation.

This module contains all input/output schemas for the order processing API.
"""

from .orders import (
    CreateOrderRequest,
    ModifyOrderRequest,
    UpdateStatusRequest,
    OrderResponse,
    OrderDetailResponse,
    OrderHistoryResponse,
    AdminOrderHistoryResponse,
    OrderStatusHistoryResponse,
)

from .shipping import (
    ShippingCalculateRequest,
    ShippingCalculateResponse,
    ShippingRatesResponse,
    ShippingItem,
    ShippingAddressInput,
    ShippingAddress,
)

from .common import (
    ErrorResponse,
    HealthResponse,
    OrderStatus,
)

__all__ = [
    # Order schemas
    "CreateOrderRequest",
    "ModifyOrderRequest",
    "UpdateStatusRequest",
    "OrderResponse",
    "OrderDetailResponse",
    "OrderHistoryResponse",
    "AdminOrderHistoryResponse",
    "OrderStatusHistoryResponse",

    # Shipping schemas
    "ShippingCalculateRequest",
    "ShippingCalculateResponse",
    "ShippingRatesResponse",
    "ShippingItem",
    "ShippingAddressInput",
    "ShippingAddress",

    # Common schemas
    "ErrorResponse",
    "HealthResponse",
    "OrderStatus",
]