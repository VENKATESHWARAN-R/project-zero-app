"""Contract tests for POST /api/v1/payments endpoint."""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from src.main import app

client = TestClient(app)


class TestPaymentsPostContract:
    """Contract tests for payment creation endpoint."""

    def test_create_payment_success(self):
        """Test successful payment creation with valid data."""
        # Valid payment request payload
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": str(uuid4()),
            "amount": 2999,  # $29.99
            "currency": "USD",
            "description": "Test payment for order"
        }
        
        # Mock JWT token (will be validated by auth middleware)
        headers = {
            "Authorization": "Bearer valid-jwt-token",
            "Content-Type": "application/json"
        }
        
        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        
        # Should return 201 Created
        assert response.status_code == 201
        
        # Validate response schema
        data = response.json()
        assert "id" in data
        assert "order_id" in data
        assert "user_id" in data
        assert "payment_method_id" in data
        assert "amount" in data
        assert "currency" in data
        assert "status" in data
        assert "gateway_transaction_id" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # Validate data types and values
        assert isinstance(data["id"], str)
        assert data["order_id"] == payment_data["order_id"]
        assert data["payment_method_id"] == payment_data["payment_method_id"]
        assert data["amount"] == payment_data["amount"]
        assert data["currency"] == payment_data["currency"]
        assert data["status"] in ["PENDING", "PROCESSING", "COMPLETED", "FAILED", "CANCELLED"]

    def test_create_payment_missing_required_fields(self):
        """Test payment creation with missing required fields."""
        # Missing order_id
        payment_data = {
            "payment_method_id": str(uuid4()),
            "amount": 2999
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400
        
        # Validate error response schema
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert "timestamp" in data

    def test_create_payment_invalid_amount(self):
        """Test payment creation with invalid amount."""
        # Zero amount
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": str(uuid4()),
            "amount": 0
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_create_payment_negative_amount(self):
        """Test payment creation with negative amount."""
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": str(uuid4()),
            "amount": -1000
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_create_payment_invalid_uuid_format(self):
        """Test payment creation with invalid UUID format."""
        payment_data = {
            "order_id": "invalid-uuid",
            "payment_method_id": str(uuid4()),
            "amount": 2999
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_create_payment_unauthorized(self):
        """Test payment creation without authorization."""
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": str(uuid4()),
            "amount": 2999
        }
        
        # No Authorization header
        response = client.post("/api/v1/payments", json=payment_data)
        
        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_create_payment_invalid_token(self):
        """Test payment creation with invalid JWT token."""
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": str(uuid4()),
            "amount": 2999
        }
        
        headers = {"Authorization": "Bearer invalid-token"}
        
        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        
        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_create_payment_duplicate_order(self):
        """Test payment creation for order that already has a payment."""
        order_id = str(uuid4())
        payment_data = {
            "order_id": order_id,
            "payment_method_id": str(uuid4()),
            "amount": 2999
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # First payment should succeed
        response1 = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert response1.status_code == 201
        
        # Second payment for same order should fail
        response2 = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert response2.status_code == 409  # Conflict

    def test_create_payment_invalid_currency(self):
        """Test payment creation with invalid currency code."""
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": str(uuid4()),
            "amount": 2999,
            "currency": "INVALID"
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_create_payment_long_description(self):
        """Test payment creation with description exceeding max length."""
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": str(uuid4()),
            "amount": 2999,
            "description": "x" * 300  # Exceeds 255 character limit
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_create_payment_content_type_validation(self):
        """Test payment creation with invalid content type."""
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": str(uuid4()),
            "amount": 2999
        }
        
        headers = {
            "Authorization": "Bearer valid-jwt-token",
            "Content-Type": "text/plain"
        }
        
        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        
        # Should return 400 Bad Request or 415 Unsupported Media Type
        assert response.status_code in [400, 415]
