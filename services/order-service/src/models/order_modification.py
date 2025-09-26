from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import Enum as SQLEnum

from ..database import Base


class ModificationType(str, Enum):
    """Types of order modifications for audit tracking."""
    STATUS_CHANGE = "STATUS_CHANGE"
    ITEM_ADDED = "ITEM_ADDED"
    ITEM_REMOVED = "ITEM_REMOVED"
    QUANTITY_CHANGED = "QUANTITY_CHANGED"
    ADDRESS_UPDATED = "ADDRESS_UPDATED"
    CANCELLATION = "CANCELLATION"
    NOTES_UPDATED = "NOTES_UPDATED"
    SHIPPING_COST_UPDATED = "SHIPPING_COST_UPDATED"


class OrderModification(Base):
    """
    OrderModification model for comprehensive audit trail.

    Tracks all changes made to orders for compliance and debugging.
    Supports JSONB storage in PostgreSQL for flexible change tracking.
    """
    __tablename__ = "order_modifications"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to order
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)

    # User who made the modification
    user_id = Column(Integer, nullable=False, index=True)
    user_email = Column(String(255), nullable=True)  # Cached for reporting

    # Modification details
    modification_type = Column(SQLEnum(ModificationType), nullable=False, index=True)
    old_value = Column(MutableDict.as_mutable(JSON), nullable=True)
    new_value = Column(MutableDict.as_mutable(JSON), nullable=True)

    # Optional reason/notes
    reason = Column(Text, nullable=True)

    # Audit timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    order = relationship("Order", back_populates="modifications")

    def __repr__(self) -> str:
        return (
            f"<OrderModification(id={self.id}, order_id={self.order_id}, "
            f"type='{self.modification_type}', created_at='{self.created_at}')>"
        )

    @classmethod
    def create_status_change(
        cls,
        order_id: int,
        user_id: int,
        user_email: Optional[str],
        old_status: str,
        new_status: str,
        reason: Optional[str] = None
    ) -> "OrderModification":
        """Create a status change modification record."""
        return cls(
            order_id=order_id,
            user_id=user_id,
            user_email=user_email,
            modification_type=ModificationType.STATUS_CHANGE,
            old_value={"status": old_status},
            new_value={"status": new_status},
            reason=reason
        )

    @classmethod
    def create_address_update(
        cls,
        order_id: int,
        user_id: int,
        user_email: Optional[str],
        old_address: Dict[str, Any],
        new_address: Dict[str, Any],
        reason: Optional[str] = None
    ) -> "OrderModification":
        """Create an address update modification record."""
        return cls(
            order_id=order_id,
            user_id=user_id,
            user_email=user_email,
            modification_type=ModificationType.ADDRESS_UPDATED,
            old_value=old_address,
            new_value=new_address,
            reason=reason
        )

    @classmethod
    def create_item_change(
        cls,
        order_id: int,
        user_id: int,
        user_email: Optional[str],
        modification_type: ModificationType,
        item_data: Dict[str, Any],
        reason: Optional[str] = None
    ) -> "OrderModification":
        """Create an item modification record (add/remove/quantity change)."""
        if modification_type == ModificationType.ITEM_ADDED:
            old_value = None
            new_value = item_data
        elif modification_type == ModificationType.ITEM_REMOVED:
            old_value = item_data
            new_value = None
        else:  # QUANTITY_CHANGED
            old_value = {"quantity": item_data.get("old_quantity")}
            new_value = {"quantity": item_data.get("new_quantity")}

        return cls(
            order_id=order_id,
            user_id=user_id,
            user_email=user_email,
            modification_type=modification_type,
            old_value=old_value,
            new_value=new_value,
            reason=reason
        )

    @classmethod
    def create_cancellation(
        cls,
        order_id: int,
        user_id: int,
        user_email: Optional[str],
        old_status: str,
        reason: Optional[str] = None
    ) -> "OrderModification":
        """Create a cancellation modification record."""
        return cls(
            order_id=order_id,
            user_id=user_id,
            user_email=user_email,
            modification_type=ModificationType.CANCELLATION,
            old_value={"status": old_status},
            new_value={"status": "CANCELLED"},
            reason=reason
        )

    @classmethod
    def create_notes_update(
        cls,
        order_id: int,
        user_id: int,
        user_email: Optional[str],
        old_notes: Optional[str],
        new_notes: Optional[str],
        reason: Optional[str] = None
    ) -> "OrderModification":
        """Create a notes update modification record."""
        return cls(
            order_id=order_id,
            user_id=user_id,
            user_email=user_email,
            modification_type=ModificationType.NOTES_UPDATED,
            old_value={"notes": old_notes},
            new_value={"notes": new_notes},
            reason=reason
        )

    def get_change_summary(self) -> str:
        """Get a human-readable summary of the change."""
        summaries = {
            ModificationType.STATUS_CHANGE: f"Status changed from {self.old_value.get('status')} to {self.new_value.get('status')}",
            ModificationType.ITEM_ADDED: f"Added item: {self.new_value.get('product_name', 'Unknown')}",
            ModificationType.ITEM_REMOVED: f"Removed item: {self.old_value.get('product_name', 'Unknown')}",
            ModificationType.QUANTITY_CHANGED: f"Changed quantity from {self.old_value.get('quantity')} to {self.new_value.get('quantity')}",
            ModificationType.ADDRESS_UPDATED: "Updated shipping address",
            ModificationType.CANCELLATION: "Order cancelled",
            ModificationType.NOTES_UPDATED: "Updated order notes",
            ModificationType.SHIPPING_COST_UPDATED: "Updated shipping cost",
        }

        return summaries.get(self.modification_type, f"Modified: {self.modification_type}")