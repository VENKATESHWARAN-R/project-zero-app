"""Unit tests for Pydantic schemas."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas import (
    CategoryEnum,
    ErrorResponse,
    HealthResponse,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)


class TestProductCreate:
    """Test ProductCreate schema validation."""

    def test_valid_product_create(self):
        """Test valid ProductCreate data."""
        data = {
            "name": "Test Product",
            "description": "A test product description",
            "price": Decimal("29.99"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
        }

        product = ProductCreate(**data)

        assert product.name == "Test Product"
        assert product.description == "A test product description"
        assert product.price == Decimal("29.99")
        assert product.category == CategoryEnum.ELECTRONICS
        assert str(product.image_url) == "https://example.com/test.jpg"
        assert product.stock_quantity == 10

    def test_missing_required_fields(self):
        """Test ProductCreate with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate()

        errors = exc_info.value.errors()
        required_fields = {
            "name",
            "description",
            "price",
            "category",
            "image_url",
            "stock_quantity",
        }
        error_fields = {error["loc"][0] for error in errors}

        assert required_fields.issubset(error_fields)

    def test_empty_name(self):
        """Test ProductCreate with empty name."""
        data = {
            "name": "",
            "description": "Test description",
            "price": Decimal("29.99"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert any("cannot be empty" in str(error) for error in exc_info.value.errors())

    def test_whitespace_only_name(self):
        """Test ProductCreate with whitespace-only name."""
        data = {
            "name": "   ",
            "description": "Test description",
            "price": Decimal("29.99"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert any("cannot be empty" in str(error) for error in exc_info.value.errors())

    def test_name_too_long(self):
        """Test ProductCreate with name exceeding max length."""
        data = {
            "name": "x" * 256,  # Exceeds 255 character limit
            "description": "Test description",
            "price": Decimal("29.99"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert any(
            "ensure this value has at most 255 characters" in str(error)
            for error in exc_info.value.errors()
        )

    def test_description_too_long(self):
        """Test ProductCreate with description exceeding max length."""
        data = {
            "name": "Test Product",
            "description": "x" * 5001,  # Exceeds 5000 character limit
            "price": Decimal("29.99"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert any(
            "ensure this value has at most 5000 characters" in str(error)
            for error in exc_info.value.errors()
        )

    def test_negative_price(self):
        """Test ProductCreate with negative price."""
        data = {
            "name": "Test Product",
            "description": "Test description",
            "price": Decimal("-10.00"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert any(
            "ensure this value is greater than 0" in str(error)
            for error in exc_info.value.errors()
        )

    def test_zero_price(self):
        """Test ProductCreate with zero price."""
        data = {
            "name": "Test Product",
            "description": "Test description",
            "price": Decimal("0.00"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert any(
            "ensure this value is greater than 0" in str(error)
            for error in exc_info.value.errors()
        )

    def test_price_too_many_decimals(self):
        """Test ProductCreate with price having too many decimal places."""
        data = {
            "name": "Test Product",
            "description": "Test description",
            "price": Decimal("29.999"),  # 3 decimal places
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert any(
            "more than 2 decimal places" in str(error)
            for error in exc_info.value.errors()
        )

    def test_invalid_category(self):
        """Test ProductCreate with invalid category."""
        data = {
            "name": "Test Product",
            "description": "Test description",
            "price": Decimal("29.99"),
            "category": "invalid_category",
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert any("Input should be" in str(error) for error in exc_info.value.errors())

    def test_invalid_url(self):
        """Test ProductCreate with invalid URL."""
        data = {
            "name": "Test Product",
            "description": "Test description",
            "price": Decimal("29.99"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "not_a_valid_url",
            "stock_quantity": 10,
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert any("URL" in str(error) for error in exc_info.value.errors())

    def test_negative_stock_quantity(self):
        """Test ProductCreate with negative stock quantity."""
        data = {
            "name": "Test Product",
            "description": "Test description",
            "price": Decimal("29.99"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": -5,
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert any(
            "ensure this value is greater than or equal to 0" in str(error)
            for error in exc_info.value.errors()
        )

    def test_string_trimming(self):
        """Test that string fields are properly trimmed."""
        data = {
            "name": "  Test Product  ",
            "description": "  Test description  ",
            "price": Decimal("29.99"),
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
        }

        product = ProductCreate(**data)

        assert product.name == "Test Product"
        assert product.description == "Test description"


class TestProductUpdate:
    """Test ProductUpdate schema validation."""

    def test_empty_update(self):
        """Test ProductUpdate with no fields (should be valid)."""
        product = ProductUpdate()

        assert product.name is None
        assert product.description is None
        assert product.price is None
        assert product.category is None
        assert product.image_url is None
        assert product.stock_quantity is None
        assert product.is_active is None

    def test_partial_update(self):
        """Test ProductUpdate with only some fields."""
        data = {
            "name": "Updated Name",
            "price": Decimal("39.99"),
        }

        product = ProductUpdate(**data)

        assert product.name == "Updated Name"
        assert product.price == Decimal("39.99")
        assert product.description is None

    def test_all_fields_update(self):
        """Test ProductUpdate with all fields."""
        data = {
            "name": "Updated Product",
            "description": "Updated description",
            "price": Decimal("49.99"),
            "category": CategoryEnum.BOOKS,
            "image_url": "https://example.com/updated.jpg",
            "stock_quantity": 25,
            "is_active": False,
        }

        product = ProductUpdate(**data)

        assert product.name == "Updated Product"
        assert product.description == "Updated description"
        assert product.price == Decimal("49.99")
        assert product.category == CategoryEnum.BOOKS
        assert str(product.image_url) == "https://example.com/updated.jpg"
        assert product.stock_quantity == 25
        assert product.is_active is False

    def test_invalid_values_validation(self):
        """Test ProductUpdate validates values same as ProductCreate."""
        # Test negative price
        with pytest.raises(ValidationError):
            ProductUpdate(price=Decimal("-10.00"))

        # Test empty string after trimming
        with pytest.raises(ValidationError):
            ProductUpdate(name="   ")

        # Test invalid URL
        with pytest.raises(ValidationError):
            ProductUpdate(image_url="not_a_url")


class TestProductResponse:
    """Test ProductResponse schema."""

    def test_valid_product_response(self):
        """Test valid ProductResponse data."""
        data = {
            "id": 1,
            "name": "Test Product",
            "description": "Test description",
            "price": 29.99,
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
            "is_active": True,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }

        product = ProductResponse(**data)

        assert product.id == 1
        assert product.name == "Test Product"
        assert product.price == 29.99
        assert product.category == CategoryEnum.ELECTRONICS


class TestProductListResponse:
    """Test ProductListResponse schema."""

    def test_valid_list_response(self):
        """Test valid ProductListResponse."""
        product_data = {
            "id": 1,
            "name": "Test Product",
            "description": "Test description",
            "price": 29.99,
            "category": CategoryEnum.ELECTRONICS,
            "image_url": "https://example.com/test.jpg",
            "stock_quantity": 10,
            "is_active": True,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }

        data = {
            "items": [ProductResponse(**product_data)],
            "total": 1,
            "offset": 0,
            "limit": 20,
            "has_more": False,
        }

        response = ProductListResponse(**data)

        assert len(response.items) == 1
        assert response.total == 1
        assert response.offset == 0
        assert response.limit == 20
        assert response.has_more is False

    def test_empty_list_response(self):
        """Test ProductListResponse with empty items."""
        data = {
            "items": [],
            "total": 0,
            "offset": 0,
            "limit": 20,
            "has_more": False,
        }

        response = ProductListResponse(**data)

        assert len(response.items) == 0
        assert response.total == 0
        assert response.has_more is False


class TestHealthResponse:
    """Test HealthResponse schema."""

    def test_basic_health_response(self):
        """Test basic health response."""
        data = {
            "status": "healthy",
            "timestamp": datetime.now(UTC),
        }

        response = HealthResponse(**data)

        assert response.status == "healthy"
        assert response.database is None

    def test_health_response_with_database(self):
        """Test health response with database status."""
        data = {
            "status": "ready",
            "timestamp": datetime.now(UTC),
            "database": "connected",
        }

        response = HealthResponse(**data)

        assert response.status == "ready"
        assert response.database == "connected"


class TestErrorResponse:
    """Test ErrorResponse schema."""

    def test_basic_error_response(self):
        """Test basic error response."""
        data = {
            "detail": "Something went wrong",
        }

        response = ErrorResponse(**data)

        assert response.detail == "Something went wrong"
        assert response.type is None

    def test_error_response_with_type(self):
        """Test error response with type."""
        data = {
            "detail": "Validation failed",
            "type": "validation_error",
        }

        response = ErrorResponse(**data)

        assert response.detail == "Validation failed"
        assert response.type == "validation_error"


class TestCategoryEnum:
    """Test CategoryEnum values."""

    def test_all_category_values(self):
        """Test all category enum values."""
        assert CategoryEnum.ELECTRONICS == "electronics"
        assert CategoryEnum.CLOTHING == "clothing"
        assert CategoryEnum.BOOKS == "books"
        assert CategoryEnum.HOME_GOODS == "home_goods"

    def test_category_enum_iteration(self):
        """Test iterating over category enum."""
        categories = list(CategoryEnum)
        expected = ["electronics", "clothing", "books", "home_goods"]

        assert len(categories) == 4
        for cat in categories:
            assert cat.value in expected
