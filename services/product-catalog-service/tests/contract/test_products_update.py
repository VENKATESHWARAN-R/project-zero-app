"""Contract tests for PUT /products/{id} endpoint."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_update_product_success():
    """Test successful product update with valid data."""
    update_data = {
        "name": "Updated Product Name",
        "price": 39.99,
    }

    headers = {"Authorization": "Bearer valid_token"}
    response = client.put("/products/1", json=update_data, headers=headers)

    assert response.status_code == 200
    data = response.json()

    # Verify updated fields
    assert data["name"] == update_data["name"]
    assert data["price"] == update_data["price"]

    # Verify complete response structure
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

    # Verify ID hasn't changed
    assert data["id"] == 1


def test_update_product_all_fields():
    """Test updating all possible fields."""
    update_data = {
        "name": "Completely Updated Product",
        "description": "Updated description",
        "price": 49.99,
        "category": "books",
        "image_url": "https://example.com/updated.jpg",
        "stock_quantity": 25,
        "is_active": False,
    }

    headers = {"Authorization": "Bearer valid_token"}
    response = client.put("/products/1", json=update_data, headers=headers)

    assert response.status_code == 200
    data = response.json()

    # Verify all fields updated
    for field, value in update_data.items():
        assert data[field] == value


def test_update_product_partial():
    """Test partial updates (only some fields)."""
    # Update only price
    headers = {"Authorization": "Bearer valid_token"}
    response = client.put("/products/1", json={"price": 99.99}, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 99.99

    # Update only name and description
    update_data = {
        "name": "New Name",
        "description": "New description",
    }
    response = client.put("/products/1", json=update_data, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]


def test_update_product_unauthorized():
    """Test product update without authentication."""
    update_data = {"name": "Updated Name"}

    response = client.put("/products/1", json=update_data)
    assert response.status_code == 401

    data = response.json()
    assert "detail" in data


def test_update_product_invalid_token():
    """Test product update with invalid token."""
    update_data = {"name": "Updated Name"}

    headers = {"Authorization": "Bearer invalid_token"}
    response = client.put("/products/1", json=update_data, headers=headers)
    assert response.status_code == 401


def test_update_product_not_found():
    """Test updating non-existent product."""
    update_data = {"name": "Updated Name"}

    headers = {"Authorization": "Bearer valid_token"}
    response = client.put("/products/99999", json=update_data, headers=headers)
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data


def test_update_product_invalid_id():
    """Test updating with invalid product ID."""
    update_data = {"name": "Updated Name"}
    headers = {"Authorization": "Bearer valid_token"}

    # Non-integer ID
    response = client.put("/products/invalid", json=update_data, headers=headers)
    assert response.status_code == 422

    # Negative ID
    response = client.put("/products/-1", json=update_data, headers=headers)
    assert response.status_code == 422

    # Zero ID
    response = client.put("/products/0", json=update_data, headers=headers)
    assert response.status_code == 422


def test_update_product_validation_errors():
    """Test product update with invalid data."""
    headers = {"Authorization": "Bearer valid_token"}

    # Invalid price
    response = client.put("/products/1", json={"price": -10.00}, headers=headers)
    assert response.status_code == 422

    # Invalid category
    response = client.put("/products/1", json={"category": "invalid"}, headers=headers)
    assert response.status_code == 422

    # Invalid URL
    response = client.put(
        "/products/1", json={"image_url": "not_a_url"}, headers=headers
    )
    assert response.status_code == 422

    # Negative stock
    response = client.put("/products/1", json={"stock_quantity": -5}, headers=headers)
    assert response.status_code == 422

    # Empty name
    response = client.put("/products/1", json={"name": ""}, headers=headers)
    assert response.status_code == 422

    # Empty description
    response = client.put("/products/1", json={"description": ""}, headers=headers)
    assert response.status_code == 422


def test_update_product_field_length_limits():
    """Test product update with field length validation."""
    headers = {"Authorization": "Bearer valid_token"}

    # Name too long
    response = client.put("/products/1", json={"name": "x" * 256}, headers=headers)
    assert response.status_code == 422

    # Description too long
    response = client.put(
        "/products/1", json={"description": "x" * 5001}, headers=headers
    )
    assert response.status_code == 422


def test_update_product_empty_body():
    """Test update with empty request body."""
    headers = {"Authorization": "Bearer valid_token"}

    # Empty JSON should be valid (no changes)
    response = client.put("/products/1", json={}, headers=headers)
    assert response.status_code == 200

    # Verify product unchanged (would need to compare with original)
    data = response.json()
    assert "id" in data
    assert data["id"] == 1


def test_update_product_readonly_fields():
    """Test that readonly fields cannot be updated."""
    headers = {"Authorization": "Bearer valid_token"}

    # Try to update ID (should be ignored or cause error)
    response = client.put("/products/1", json={"id": 999}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # ID should remain unchanged
        assert data["id"] == 1
    else:
        # Or it might return validation error
        assert response.status_code == 422

    # Try to update created_at (should be ignored)
    response = client.put(
        "/products/1", json={"created_at": "2025-01-01T00:00:00Z"}, headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        # created_at should not change to the provided value
        assert data["created_at"] != "2025-01-01T00:00:00Z"
