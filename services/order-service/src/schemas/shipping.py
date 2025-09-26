"""
Shipping-related schemas for API validation.
"""

import re
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class ShippingItem(BaseModel):
    """Item for shipping calculation."""
    weight: float = Field(..., gt=0, description="Item weight in pounds")
    quantity: int = Field(..., gt=0, description="Quantity of items")


class ShippingAddressInput(BaseModel):
    """Shipping address input validation."""
    recipient_name: str = Field(..., min_length=1, max_length=100, description="Recipient name")
    company: Optional[str] = Field(None, max_length=100, description="Company name")
    address_line_1: str = Field(..., min_length=1, max_length=200, description="Primary address line")
    address_line_2: Optional[str] = Field(None, max_length=200, description="Secondary address line")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    state_province: str = Field(..., min_length=1, max_length=100, description="State or province")
    postal_code: str = Field(..., min_length=1, max_length=20, description="ZIP or postal code")
    country: str = Field(..., description="ISO 3166-1 alpha-2 country code")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    delivery_instructions: Optional[str] = Field(None, max_length=500, description="Special delivery instructions")

    @field_validator("country")
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """Validate country code format."""
        if not re.match(r"^[A-Z]{2}$", v.upper()):
            raise ValueError("Country must be a valid ISO 3166-1 alpha-2 code")
        return v.upper()

    @field_validator("phone")
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        """Basic phone number validation."""
        if v is None:
            return v

        # Remove spaces, hyphens, parentheses for validation
        clean_phone = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(r"^[\+]?[1-9][\d]{8,15}$", clean_phone):
            raise ValueError("Invalid phone number format")
        return v


class ShippingAddress(ShippingAddressInput):
    """Shipping address with ID for responses."""
    id: int = Field(..., description="Address ID")


class ShippingCalculateRequest(BaseModel):
    """Request for shipping cost calculation."""
    items: List[ShippingItem] = Field(..., min_length=1, description="Items to ship")
    address: ShippingAddressInput = Field(..., description="Delivery address")


class ShippingCalculateResponse(BaseModel):
    """Response for shipping cost calculation."""
    shipping_cost: float = Field(..., description="Calculated shipping cost")
    shipping_tier: str = Field(..., description="Shipping tier (Light, Medium, Heavy, Freight)")
    total_weight: float = Field(..., description="Total weight of items")
    zone: Optional[str] = Field(None, description="Shipping zone")


class ShippingRate(BaseModel):
    """Shipping rate configuration."""
    name: str = Field(..., description="Rate tier name")
    max_weight: float = Field(..., description="Maximum weight for this tier")
    base_rate: float = Field(..., description="Base shipping rate")


class ShippingRatesResponse(BaseModel):
    """Response with available shipping rates."""
    rates: List[ShippingRate] = Field(..., description="Available shipping rates")