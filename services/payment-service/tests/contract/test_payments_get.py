"""Contract tests for GET /api/v1/payments endpoint."""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestPaymentsGetContract:
    """Contract tests for payment history endpoint."""

    def test_get_payments_success(self):
        """Test successful retrieval of payment history."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get("/api/v1/payments", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Validate response schema
        data = response.json()
        assert "payments" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        
        # Validate data types
        assert isinstance(data["payments"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["limit"], int)
        assert isinstance(data["offset"], int)
        
        # Validate default pagination
        assert data["limit"] == 20  # Default limit
        assert data["offset"] == 0   # Default offset

    def test_get_payments_with_pagination(self):
        """Test payment history with pagination parameters."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        params = {"limit": 10, "offset": 5}
        
        response = client.get("/api/v1/payments", headers=headers, params=params)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Validate pagination parameters are respected
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 5

    def test_get_payments_with_status_filter(self):
        """Test payment history with status filter."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        params = {"status": "COMPLETED"}
        
        response = client.get("/api/v1/payments", headers=headers, params=params)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Validate response structure
        data = response.json()
        assert "payments" in data
        
        # All returned payments should have COMPLETED status
        for payment in data["payments"]:
            assert payment["status"] == "COMPLETED"

    def test_get_payments_invalid_limit(self):
        """Test payment history with invalid limit parameter."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Test limit too high
        params = {"limit": 150}  # Max is 100
        response = client.get("/api/v1/payments", headers=headers, params=params)
        assert response.status_code == 400
        
        # Test limit too low
        params = {"limit": 0}  # Min is 1
        response = client.get("/api/v1/payments", headers=headers, params=params)
        assert response.status_code == 400

    def test_get_payments_invalid_offset(self):
        """Test payment history with invalid offset parameter."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        params = {"offset": -1}  # Min is 0
        
        response = client.get("/api/v1/payments", headers=headers, params=params)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_get_payments_invalid_status_filter(self):
        """Test payment history with invalid status filter."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        params = {"status": "INVALID_STATUS"}
        
        response = client.get("/api/v1/payments", headers=headers, params=params)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_get_payments_unauthorized(self):
        """Test payment history without authorization."""
        response = client.get("/api/v1/payments")
        
        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_get_payments_invalid_token(self):
        """Test payment history with invalid JWT token."""
        headers = {"Authorization": "Bearer invalid-token"}
        
        response = client.get("/api/v1/payments", headers=headers)
        
        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_get_payments_payment_schema_validation(self):
        """Test that individual payment objects have correct schema."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get("/api/v1/payments", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # If payments exist, validate their schema
        for payment in data["payments"]:
            # Required fields
            assert "id" in payment
            assert "order_id" in payment
            assert "user_id" in payment
            assert "payment_method_id" in payment
            assert "amount" in payment
            assert "currency" in payment
            assert "status" in payment
            assert "created_at" in payment
            assert "updated_at" in payment
            
            # Validate data types
            assert isinstance(payment["id"], str)
            assert isinstance(payment["order_id"], str)
            assert isinstance(payment["user_id"], str)
            assert isinstance(payment["payment_method_id"], str)
            assert isinstance(payment["amount"], int)
            assert isinstance(payment["currency"], str)
            assert isinstance(payment["status"], str)
            assert isinstance(payment["created_at"], str)
            assert isinstance(payment["updated_at"], str)
            
            # Validate enum values
            assert payment["status"] in [
                "PENDING", "PROCESSING", "COMPLETED", "FAILED", "CANCELLED", "REFUNDED"
            ]

    def test_get_payments_empty_result(self):
        """Test payment history when user has no payments."""
        headers = {"Authorization": "Bearer valid-jwt-token-no-payments"}
        
        response = client.get("/api/v1/payments", headers=headers)
        
        # Should return 200 OK with empty list
        assert response.status_code == 200
        
        data = response.json()
        assert data["payments"] == []
        assert data["total"] == 0

    def test_get_payments_multiple_status_filters(self):
        """Test payment history with multiple status values (if supported)."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Some APIs might support multiple status filters
        # This test documents the expected behavior
        params = {"status": "COMPLETED,FAILED"}
        
        response = client.get("/api/v1/payments", headers=headers, params=params)
        
        # Behavior depends on implementation:
        # Either 200 with filtered results or 400 for unsupported format
        assert response.status_code in [200, 400]

    def test_get_payments_large_offset(self):
        """Test payment history with large offset value."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        params = {"offset": 10000}
        
        response = client.get("/api/v1/payments", headers=headers, params=params)
        
        # Should return 200 OK with empty results
        assert response.status_code == 200
        
        data = response.json()
        assert data["payments"] == []
