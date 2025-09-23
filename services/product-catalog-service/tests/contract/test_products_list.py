"""Contract tests for GET /products endpoint."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_list_products_success():
    """Test successful product listing with default pagination."""
    response = client.get("/products")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure matches contract
    assert "items" in data
    assert "total" in data
    assert "offset" in data
    assert "limit" in data
    assert "has_more" in data

    # Verify types
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)
    assert isinstance(data["offset"], int)
    assert isinstance(data["limit"], int)
    assert isinstance(data["has_more"], bool)

    # Verify pagination defaults
    assert data["offset"] == 0
    assert data["limit"] == 20


def test_list_products_with_pagination():
    """Test product listing with custom pagination parameters."""
    response = client.get("/products?offset=10&limit=5")

    assert response.status_code == 200
    data = response.json()

    assert data["offset"] == 10
    assert data["limit"] == 5


def test_list_products_invalid_pagination():
    """Test product listing with invalid pagination parameters."""
    # Negative offset
    response = client.get("/products?offset=-1")
    assert response.status_code == 400

    # Limit too large
    response = client.get("/products?limit=101")
    assert response.status_code == 400

    # Invalid types
    response = client.get("/products?offset=invalid")
    assert response.status_code == 422


def test_list_products_product_structure():
    """Test that products in list have correct structure."""
    response = client.get("/products?limit=1")

    assert response.status_code == 200
    data = response.json()

    if data["items"]:
        product = data["items"][0]

        # Required fields from OpenAPI spec
        required_fields = [
            "id",
            "name",
            "description",
            "price",
            "category",
            "image_url",
            "stock_quantity",
            "is_active",
            "created_at",
            "updated_at",
        ]

        for field in required_fields:
            assert field in product

        # Verify types
        assert isinstance(product["id"], int)
        assert isinstance(product["name"], str)
        assert isinstance(product["description"], str)
        assert isinstance(product["price"], (int, float))
        assert isinstance(product["category"], str)
        assert isinstance(product["image_url"], str)
        assert isinstance(product["stock_quantity"], int)
        assert isinstance(product["is_active"], bool)
        assert isinstance(product["created_at"], str)
        assert isinstance(product["updated_at"], str)

        # Verify category enum
        valid_categories = ["electronics", "clothing", "books", "home_goods"]
        assert product["category"] in valid_categories
