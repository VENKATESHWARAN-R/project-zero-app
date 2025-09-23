"""Contract tests for POST /products endpoint."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_create_product_success():
    """Test successful product creation with valid data."""
    product_data = {
        "name": "Test Product",
        "description": "A test product for contract testing",
        "price": 29.99,
        "category": "electronics",
        "image_url": "https://example.com/test.jpg",
        "stock_quantity": 10,
    }

    # Mock auth token (will fail until auth middleware is implemented)
    headers = {"Authorization": "Bearer valid_token"}
    response = client.post("/products", json=product_data, headers=headers)

    assert response.status_code == 201
    data = response.json()

    # Verify response structure
    assert "id" in data
    assert data["name"] == product_data["name"]
    assert data["description"] == product_data["description"]
    assert data["price"] == product_data["price"]
    assert data["category"] == product_data["category"]
    assert data["image_url"] == product_data["image_url"]
    assert data["stock_quantity"] == product_data["stock_quantity"]
    assert data["is_active"] is True  # Default value
    assert "created_at" in data
    assert "updated_at" in data


def test_create_product_unauthorized():
    """Test product creation without authentication."""
    product_data = {
        "name": "Test Product",
        "description": "A test product",
        "price": 29.99,
        "category": "electronics",
        "image_url": "https://example.com/test.jpg",
        "stock_quantity": 10,
    }

    response = client.post("/products", json=product_data)
    assert response.status_code == 401

    data = response.json()
    assert "detail" in data


def test_create_product_invalid_token():
    """Test product creation with invalid token."""
    product_data = {
        "name": "Test Product",
        "description": "A test product",
        "price": 29.99,
        "category": "electronics",
        "image_url": "https://example.com/test.jpg",
        "stock_quantity": 10,
    }

    headers = {"Authorization": "Bearer invalid_token"}
    response = client.post("/products", json=product_data, headers=headers)
    assert response.status_code == 401


def test_create_product_validation_errors():
    """Test product creation with invalid data."""
    headers = {"Authorization": "Bearer valid_token"}

    # Missing required fields
    response = client.post("/products", json={}, headers=headers)
    assert response.status_code == 422

    # Invalid price
    invalid_data = {
        "name": "Test Product",
        "description": "A test product",
        "price": -10.00,  # Negative price
        "category": "electronics",
        "image_url": "https://example.com/test.jpg",
        "stock_quantity": 10,
    }
    response = client.post("/products", json=invalid_data, headers=headers)
    assert response.status_code == 422

    # Invalid category
    invalid_data["price"] = 29.99
    invalid_data["category"] = "invalid_category"
    response = client.post("/products", json=invalid_data, headers=headers)
    assert response.status_code == 422

    # Invalid URL format
    invalid_data["category"] = "electronics"
    invalid_data["image_url"] = "not_a_valid_url"
    response = client.post("/products", json=invalid_data, headers=headers)
    assert response.status_code == 422

    # Negative stock
    invalid_data["image_url"] = "https://example.com/test.jpg"
    invalid_data["stock_quantity"] = -5
    response = client.post("/products", json=invalid_data, headers=headers)
    assert response.status_code == 422


def test_create_product_field_length_limits():
    """Test product creation with field length validation."""
    headers = {"Authorization": "Bearer valid_token"}

    # Name too long
    long_name_data = {
        "name": "x" * 256,  # Max is 255
        "description": "A test product",
        "price": 29.99,
        "category": "electronics",
        "image_url": "https://example.com/test.jpg",
        "stock_quantity": 10,
    }
    response = client.post("/products", json=long_name_data, headers=headers)
    assert response.status_code == 422

    # Description too long
    long_desc_data = {
        "name": "Test Product",
        "description": "x" * 5001,  # Max is 5000
        "price": 29.99,
        "category": "electronics",
        "image_url": "https://example.com/test.jpg",
        "stock_quantity": 10,
    }
    response = client.post("/products", json=long_desc_data, headers=headers)
    assert response.status_code == 422


def test_create_product_empty_strings():
    """Test product creation with empty string validation."""
    headers = {"Authorization": "Bearer valid_token"}

    empty_name_data = {
        "name": "",
        "description": "A test product",
        "price": 29.99,
        "category": "electronics",
        "image_url": "https://example.com/test.jpg",
        "stock_quantity": 10,
    }
    response = client.post("/products", json=empty_name_data, headers=headers)
    assert response.status_code == 422

    empty_desc_data = {
        "name": "Test Product",
        "description": "",
        "price": 29.99,
        "category": "electronics",
        "image_url": "https://example.com/test.jpg",
        "stock_quantity": 10,
    }
    response = client.post("/products", json=empty_desc_data, headers=headers)
    assert response.status_code == 422
