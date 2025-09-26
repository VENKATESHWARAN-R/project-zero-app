"""
Order-related schemas for API validation.
"""

from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field

from .common import OrderStatus
from .shipping import ShippingAddressInput, ShippingAddress


class CreateOrderRequest(BaseModel):
    """Request to create a new order."""
    shipping_address: ShippingAddressInput = Field(..., description="Shipping address")
    notes: Optional[str] = Field(None, max_length=500, description="Order notes")


class ModifyOrderRequest(BaseModel):
    """Request to modify an existing order."""
    shipping_address: Optional[ShippingAddressInput] = Field(None, description="Updated shipping address")
    notes: Optional[str] = Field(None, max_length=500, description="Updated order notes")


class UpdateStatusRequest(BaseModel):
    """Request to update order status."""
    status: OrderStatus = Field(..., description="New order status")
    notes: Optional[str] = Field(None, max_length=500, description="Status update notes")


class OrderItem(BaseModel):
    """Order item for responses."""
    id: int = Field(..., description="Order item ID")
    product_id: int = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    product_sku: Optional[str] = Field(None, description="Product SKU")
    quantity: int = Field(..., description="Quantity ordered")
    unit_price: float = Field(..., description="Unit price at time of order")
    total_price: float = Field(..., description="Total price for this item")
    weight: float = Field(..., description="Item weight")


class OrderResponse(BaseModel):
    """Basic order response."""
    id: int = Field(..., description="Order ID")
    order_number: str = Field(..., description="Human-readable order number")
    user_id: int = Field(..., description="User ID who placed the order")
    status: OrderStatus = Field(..., description="Current order status")
    subtotal: float = Field(..., description="Order subtotal")
    tax_rate: float = Field(..., description="Applied tax rate")
    tax_amount: float = Field(..., description="Tax amount")
    shipping_cost: float = Field(..., description="Shipping cost")
    total: float = Field(..., description="Total order amount")
    currency: str = Field(..., description="Currency code")
    created_at: datetime = Field(..., description="Order creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    modification_count: int = Field(..., description="Number of modifications made")


class OrderDetailResponse(OrderResponse):
    """Detailed order response with items and shipping address."""
    items: List[OrderItem] = Field(..., description="Order items")
    shipping_address: ShippingAddress = Field(..., description="Shipping address")


class OrderHistoryResponse(BaseModel):
    """Response for order history with pagination."""
    orders: List[OrderResponse] = Field(..., description="List of orders")
    total: int = Field(..., description="Total number of orders")
    limit: int = Field(..., description="Maximum orders returned")
    offset: int = Field(..., description="Number of orders skipped")


class AdminOrderResponse(OrderResponse):
    """Order response for admin view with additional fields."""
    user_email: Optional[str] = Field(None, description="Customer email for admin view")


class AdminOrderHistoryResponse(BaseModel):
    """Response for admin order history with user information."""
    orders: List[AdminOrderResponse] = Field(..., description="List of orders with user info")
    total: int = Field(..., description="Total number of orders")
    limit: int = Field(..., description="Maximum orders returned")
    offset: int = Field(..., description="Number of orders skipped")


class OrderStatusChange(BaseModel):
    """Order status change record."""
    status: OrderStatus = Field(..., description="Order status")
    timestamp: datetime = Field(..., description="Status change timestamp")
    notes: Optional[str] = Field(None, description="Status change notes")
    updated_by: str = Field(..., description="User who made the change")


class OrderStatusHistoryResponse(BaseModel):
    """Response for order status history."""
    order_id: int = Field(..., description="Order ID")
    status_history: List[OrderStatusChange] = Field(..., description="Status change history")