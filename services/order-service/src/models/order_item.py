from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class OrderItem(Base):
    """
    OrderItem model representing individual products within an order.

    Captures product snapshots at order time to preserve pricing and details
    even if the original product changes.
    """
    __tablename__ = "order_items"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to order
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)

    # Product information (snapshot at order time)
    product_id = Column(Integer, nullable=False, index=True)  # Reference to product catalog
    product_name = Column(String(200), nullable=False)
    product_sku = Column(String(100), nullable=True)

    # Quantity and pricing
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)

    # Physical properties for shipping calculations
    weight = Column(Numeric(8, 2), nullable=False)  # Weight in pounds

    # Audit timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")

    def __repr__(self) -> str:
        return (
            f"<OrderItem(id={self.id}, order_id={self.order_id}, "
            f"product_name='{self.product_name}', quantity={self.quantity}, "
            f"total_price={self.total_price})>"
        )

    def calculate_total_price(self) -> None:
        """Calculate total price based on quantity and unit price."""
        self.total_price = Decimal(str(self.quantity)) * self.unit_price

    def calculate_total_weight(self) -> Decimal:
        """Calculate total weight for this item."""
        return Decimal(str(self.quantity)) * self.weight

    @property
    def display_name(self) -> str:
        """Get display name with SKU if available."""
        if self.product_sku:
            return f"{self.product_name} ({self.product_sku})"
        return self.product_name

    def validate_quantities(self) -> bool:
        """Validate that quantities and prices are positive."""
        return (
            self.quantity > 0
            and self.unit_price > 0
            and self.weight >= 0
            and self.total_price == (Decimal(str(self.quantity)) * self.unit_price)
        )