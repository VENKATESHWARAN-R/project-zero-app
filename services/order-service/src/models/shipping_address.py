import re
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class ShippingAddress(Base):
    """
    ShippingAddress model for customer delivery locations.

    Contains complete address information with validation for deliverability.
    One-to-one relationship with Order.
    """
    __tablename__ = "shipping_addresses"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to order (one-to-one)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True, index=True)

    # Recipient information
    recipient_name = Column(String(100), nullable=False)
    company = Column(String(100), nullable=True)

    # Address components
    address_line_1 = Column(String(200), nullable=False)
    address_line_2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=False)
    state_province = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(2), nullable=False)  # ISO 3166-1 alpha-2

    # Contact information
    phone = Column(String(20), nullable=True)

    # Delivery instructions
    delivery_instructions = Column(Text, nullable=True)

    # Audit timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    order = relationship("Order", back_populates="shipping_address")

    def __repr__(self) -> str:
        return (
            f"<ShippingAddress(id={self.id}, order_id={self.order_id}, "
            f"recipient_name='{self.recipient_name}', city='{self.city}')>"
        )

    @property
    def full_address(self) -> str:
        """Get formatted full address string."""
        lines = [self.address_line_1]

        if self.address_line_2:
            lines.append(self.address_line_2)

        lines.append(f"{self.city}, {self.state_province} {self.postal_code}")
        lines.append(self.country.upper())

        return "\n".join(lines)

    @property
    def display_name(self) -> str:
        """Get recipient display name with company if available."""
        if self.company:
            return f"{self.recipient_name}, {self.company}"
        return self.recipient_name

    def validate_country_code(self) -> bool:
        """Validate that country code is a valid ISO 3166-1 alpha-2 code."""
        return bool(re.match(r"^[A-Z]{2}$", self.country))

    def validate_postal_code(self) -> bool:
        """Basic postal code validation based on country."""
        if not self.postal_code:
            return False

        postal_patterns = {
            "US": r"^\d{5}(-\d{4})?$",  # 12345 or 12345-6789
            "CA": r"^[A-Z]\d[A-Z] ?\d[A-Z]\d$",  # A1A 1A1 or A1A1A1
            "GB": r"^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$",  # UK postcodes
            # Add more patterns as needed
        }

        pattern = postal_patterns.get(self.country)
        if pattern:
            return bool(re.match(pattern, self.postal_code.upper()))

        # For unknown countries, just check it's not empty
        return len(self.postal_code.strip()) > 0

    def validate_phone_number(self) -> bool:
        """Basic phone number validation if provided."""
        if not self.phone:
            return True  # Optional field

        # Basic validation: starts with + and contains only digits, spaces, hyphens, parentheses
        phone_pattern = r"^[\+]?[1-9][\d\s\-\(\)]{8,15}$"
        return bool(re.match(phone_pattern, self.phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")))

    def validate_address(self) -> dict[str, bool]:
        """Comprehensive address validation."""
        return {
            "recipient_name": bool(self.recipient_name and self.recipient_name.strip()),
            "address_line_1": bool(self.address_line_1 and self.address_line_1.strip()),
            "city": bool(self.city and self.city.strip()),
            "state_province": bool(self.state_province and self.state_province.strip()),
            "postal_code": self.validate_postal_code(),
            "country": self.validate_country_code(),
            "phone": self.validate_phone_number(),
        }

    def is_valid(self) -> bool:
        """Check if address meets all validation requirements."""
        validation_results = self.validate_address()
        return all(validation_results.values())