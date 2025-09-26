"""
Order service database models.

This module contains all SQLAlchemy models for the order processing service.
Models are designed to work with both SQLite (development) and PostgreSQL (production).
"""

from .order import Order, OrderStatus
from .order_item import OrderItem
from .shipping_address import ShippingAddress
from .order_modification import OrderModification, ModificationType

# Export all models for easy importing
__all__ = [
    "Order",
    "OrderStatus",
    "OrderItem",
    "ShippingAddress",
    "OrderModification",
    "ModificationType",
]


def get_all_models():
    """Get all model classes for database operations."""
    return [Order, OrderItem, ShippingAddress, OrderModification]