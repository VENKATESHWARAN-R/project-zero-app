"""Contract tests for GET /products/{id} endpoint."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_get_product_success():
    """Test successful retrieval of existing product."""
    # Assuming product with ID 1 exists
    response = client.get("/products/1")

    assert response.status_code == 200
    data = response.json()

    # Verify complete product structure from contract
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
        assert field in data

    # Verify types match OpenAPI spec
    assert isinstance(data["id"], int)
    assert isinstance(data["name"], str)
    assert isinstance(data["description"], str)
    assert isinstance(data["price"], (int, float))
    assert isinstance(data["category"], str)
    assert isinstance(data["image_url"], str)
    assert isinstance(data["stock_quantity"], int)
    assert isinstance(data["is_active"], bool)
    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)

    # Verify constraints
    assert data["id"] == 1
    assert len(data["name"]) > 0
    assert len(data["description"]) > 0
    assert data["price"] > 0
    assert data["category"] in ["electronics", "clothing", "books", "home_goods"]
    assert data["stock_quantity"] >= 0


def test_get_product_not_found():
    """Test retrieval of non-existent product."""
    # Use a very high ID that shouldn't exist
    response = client.get("/products/99999")

    assert response.status_code == 404
    data = response.json()

    assert "detail" in data
    assert isinstance(data["detail"], str)


def test_get_product_invalid_id():
    """Test retrieval with invalid product ID formats."""
    # Non-integer ID
    response = client.get("/products/invalid")
    assert response.status_code == 422

    # Negative ID
    response = client.get("/products/-1")
    assert response.status_code == 422

    # Zero ID
    response = client.get("/products/0")
    assert response.status_code == 422

    # Float ID (should be handled by path parameter validation)
    response = client.get("/products/1.5")
    assert response.status_code == 422


def test_get_product_response_format():
    """Test that response format matches exact contract specification."""
    response = client.get("/products/1")

    if response.status_code == 200:
        data = response.json()

        # Verify no extra fields beyond contract
        expected_fields = {
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
        }
        actual_fields = set(data.keys())

        # Should have exactly the expected fields
        assert actual_fields == expected_fields

        # Verify datetime format (ISO 8601)
        import re

        iso_pattern = (
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
        )
        assert re.match(iso_pattern, data["created_at"])
        assert re.match(iso_pattern, data["updated_at"])

        # Verify decimal precision for price
        if isinstance(data["price"], float):
            # Should have at most 2 decimal places
            price_str = f"{data['price']:.2f}"
            assert float(price_str) == data["price"]


def test_get_product_inactive_visibility():
    """Test that inactive products are still visible in direct get."""
    # This test will need to be updated once we have inactive products
    # For now, just verify the endpoint works
    response = client.get("/products/1")

    # Should get 200 or 404, not other errors
    assert response.status_code in [200, 404]
