"""Pydantic schemas for product data validation."""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl, field_validator


class CategoryEnum(str, Enum):
    """Product category enumeration for API."""

    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    BOOKS = "books"
    HOME_GOODS = "home_goods"


class ProductCreate(BaseModel):
    """Schema for creating a new product."""

    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: str = Field(
        ..., min_length=1, max_length=5000, description="Product description"
    )
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Product price")
    category: CategoryEnum = Field(..., description="Product category")
    image_url: HttpUrl = Field(..., description="URL to product image")
    stock_quantity: int = Field(..., ge=0, description="Initial stock quantity")

    @field_validator("name", "description")
    @classmethod
    def validate_strings(cls, v):
        """Validate string fields are not empty after stripping."""
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Field cannot be empty")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        """Ensure price has at most 2 decimal places."""
        if v.as_tuple().exponent < -2:
            raise ValueError("Price cannot have more than 2 decimal places")
        return v


class ProductUpdate(BaseModel):
    """Schema for updating an existing product."""

    name: str | None = Field(
        None, min_length=1, max_length=255, description="Product name"
    )
    description: str | None = Field(
        None, min_length=1, max_length=5000, description="Product description"
    )
    price: Decimal | None = Field(
        None, gt=0, decimal_places=2, description="Product price"
    )
    category: CategoryEnum | None = Field(None, description="Product category")
    image_url: HttpUrl | None = Field(None, description="URL to product image")
    stock_quantity: int | None = Field(None, ge=0, description="Stock quantity")
    is_active: bool | None = Field(
        None, description="Whether product is active/visible"
    )

    @field_validator("name", "description")
    @classmethod
    def validate_strings(cls, v):
        """Validate string fields are not empty after stripping."""
        if v is not None and isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Field cannot be empty")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        """Ensure price has at most 2 decimal places."""
        if v is not None and v.as_tuple().exponent < -2:
            raise ValueError("Price cannot have more than 2 decimal places")
        return v


class ProductResponse(BaseModel):
    """Schema for product response."""

    id: int = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Product description")
    price: float = Field(..., description="Product price")
    category: CategoryEnum = Field(..., description="Product category")
    image_url: str = Field(..., description="URL to product image")
    stock_quantity: int = Field(..., description="Available stock quantity")
    is_active: bool = Field(..., description="Whether product is active/visible")
    created_at: datetime = Field(..., description="Product creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Schema for paginated product list response."""

    items: list[ProductResponse] = Field(..., description="List of products")
    total: int = Field(..., description="Total number of products matching criteria")
    offset: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum items in response")
    has_more: bool = Field(..., description="Whether more items are available")


class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    database: str | None = Field(None, description="Database connection status")


class ErrorResponse(BaseModel):
    """Schema for error response."""

    detail: str = Field(..., description="Error message")
    type: str | None = Field(None, description="Error type")
