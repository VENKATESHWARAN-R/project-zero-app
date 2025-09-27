"""Contract tests for GET /api/v1/payments/{payment_id} endpoint."""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from src.main import app

client = TestClient(app)


class TestPaymentDetailsContract:
    """Contract tests for payment details endpoint."""

    def test_get_payment_details_success(self):
        """Test successful retrieval of payment details."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Validate response schema
        data = response.json()
        
        # Required fields
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
        
        # Optional fields
        assert "failure_reason" in data or data.get("failure_reason") is None
        assert "processed_at" in data or data.get("processed_at") is None
        
        # Validate data types
        assert isinstance(data["id"], str)
        assert isinstance(data["order_id"], str)
        assert isinstance(data["user_id"], str)
        assert isinstance(data["payment_method_id"], str)
        assert isinstance(data["amount"], int)
        assert isinstance(data["currency"], str)
        assert isinstance(data["status"], str)
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
        
        # Validate enum values
        assert data["status"] in [
            "PENDING", "PROCESSING", "COMPLETED", "FAILED", "CANCELLED", "REFUNDED"
        ]
        
        # Validate that returned ID matches requested ID
        assert data["id"] == payment_id

    def test_get_payment_details_not_found(self):
        """Test retrieval of non-existent payment."""
        non_existent_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{non_existent_id}", headers=headers)
        
        # Should return 404 Not Found
        assert response.status_code == 404
        
        # Validate error response schema
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert "timestamp" in data

    def test_get_payment_details_invalid_uuid(self):
        """Test retrieval with invalid UUID format."""
        invalid_id = "invalid-uuid-format"
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{invalid_id}", headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_get_payment_details_unauthorized(self):
        """Test payment details retrieval without authorization."""
        payment_id = str(uuid4())
        
        response = client.get(f"/api/v1/payments/{payment_id}")
        
        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_get_payment_details_invalid_token(self):
        """Test payment details retrieval with invalid JWT token."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer invalid-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
        
        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_get_payment_details_forbidden_access(self):
        """Test access to payment belonging to different user."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token-different-user"}
        
        response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
        
        # Should return 404 Not Found (not 403 to avoid information disclosure)
        assert response.status_code == 404

    def test_get_payment_details_completed_payment(self):
        """Test retrieval of completed payment with all fields populated."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # For completed payments, processed_at should be present
        if data["status"] == "COMPLETED":
            assert "processed_at" in data
            assert data["processed_at"] is not None
            assert isinstance(data["processed_at"], str)

    def test_get_payment_details_failed_payment(self):
        """Test retrieval of failed payment with failure reason."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # For failed payments, failure_reason should be present
        if data["status"] == "FAILED":
            assert "failure_reason" in data
            assert data["failure_reason"] is not None
            assert isinstance(data["failure_reason"], str)

    def test_get_payment_details_gateway_transaction_id(self):
        """Test that gateway transaction ID is present and valid format."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Gateway transaction ID should be present
        assert "gateway_transaction_id" in data
        assert isinstance(data["gateway_transaction_id"], str)
        assert len(data["gateway_transaction_id"]) > 0

    def test_get_payment_details_timestamp_format(self):
        """Test that timestamps are in correct ISO format."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Validate timestamp formats (ISO 8601)
        import datetime
        
        # created_at should be valid ISO format
        try:
            datetime.datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("created_at is not in valid ISO format")
        
        # updated_at should be valid ISO format
        try:
            datetime.datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("updated_at is not in valid ISO format")
        
        # processed_at should be valid ISO format if present
        if data.get("processed_at"):
            try:
                datetime.datetime.fromisoformat(data["processed_at"].replace('Z', '+00:00'))
            except ValueError:
                pytest.fail("processed_at is not in valid ISO format")

    def test_get_payment_details_amount_validation(self):
        """Test that amount is positive integer in cents."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Amount should be positive integer
        assert isinstance(data["amount"], int)
        assert data["amount"] > 0

    def test_get_payment_details_currency_validation(self):
        """Test that currency is valid ISO code."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Currency should be valid 3-letter code
        assert isinstance(data["currency"], str)
        assert len(data["currency"]) == 3
        assert data["currency"].isupper()
        # For this implementation, should be USD
        assert data["currency"] == "USD"
