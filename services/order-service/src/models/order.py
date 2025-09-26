from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class OrderStatus(str, Enum):
    """Order lifecycle status enumeration."""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class Order(Base):
    """
    Order model representing a customer's purchase commitment.

    Handles complete lifecycle tracking from creation to delivery/cancellation.
    """
    __tablename__ = "orders"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # User and identification
    user_id = Column(Integer, nullable=False, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)

    # Order status and lifecycle
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)

    # Financial calculations (using Numeric for precision)
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_rate = Column(Numeric(5, 4), nullable=False)  # e.g., 0.0850 for 8.5%
    tax_amount = Column(Numeric(10, 2), nullable=False)
    shipping_cost = Column(Numeric(10, 2), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)

    # Currency and metadata
    currency = Column(String(3), default="USD", nullable=False)
    modification_count = Column(Integer, default=0, nullable=False)

    # Optional notes
    notes = Column(Text, nullable=True)

    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    shipping_address = relationship("ShippingAddress", back_populates="order", uselist=False, cascade="all, delete-orphan")
    modifications = relationship("OrderModification", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, order_number='{self.order_number}', status='{self.status}', total={self.total})>"

    @property
    def is_modifiable(self) -> bool:
        """Check if order can be modified based on current status."""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]

    @property
    def is_cancellable(self) -> bool:
        """Check if order can be cancelled based on current status."""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PROCESSING]

    def calculate_totals(self, tax_rate: Optional[Decimal] = None) -> None:
        """
        Calculate order totals based on items and tax rate.

        Args:
            tax_rate: Optional tax rate override, otherwise uses current tax_rate
        """
        if not self.items:
            self.subtotal = Decimal("0.00")
            self.tax_amount = Decimal("0.00")
            self.total = self.shipping_cost or Decimal("0.00")
            return

        # Calculate subtotal from items
        self.subtotal = sum(item.total_price for item in self.items)

        # Use provided tax rate or current tax rate
        if tax_rate is not None:
            self.tax_rate = tax_rate

        # Calculate tax amount
        self.tax_amount = self.subtotal * self.tax_rate

        # Calculate final total
        shipping = self.shipping_cost or Decimal("0.00")
        self.total = self.subtotal + self.tax_amount + shipping

    def can_transition_to(self, new_status: OrderStatus) -> bool:
        """
        Validate if order can transition to new status.

        Valid transitions:
        - PENDING → CONFIRMED, CANCELLED
        - CONFIRMED → PROCESSING, CANCELLED
        - PROCESSING → SHIPPED, CANCELLED
        - SHIPPED → DELIVERED
        - DELIVERED, CANCELLED → No transitions (final states)
        """
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [],
            OrderStatus.CANCELLED: [],
        }

        return new_status in valid_transitions.get(self.status, [])