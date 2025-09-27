"""Contract tests for GET /api/v1/payments/{payment_id}/status endpoint."""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from src.main import app

client = TestClient(app)


class TestPaymentStatusContract:
    """Contract tests for payment status endpoint."""

    def test_get_payment_status_success(self):
        """Test successful retrieval of payment status."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}/status", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Validate response schema
        data = response.json()
        
        # Required fields
        assert "payment_id" in data
        assert "status" in data
        assert "updated_at" in data
        
        # Validate data types
        assert isinstance(data["payment_id"], str)
        assert isinstance(data["status"], str)
        assert isinstance(data["updated_at"], str)
        
        # Validate that returned payment_id matches requested ID
        assert data["payment_id"] == payment_id
        
        # Validate enum values
        assert data["status"] in [
            "PENDING", "PROCESSING", "COMPLETED", "FAILED", "CANCELLED", "REFUNDED"
        ]

    def test_get_payment_status_not_found(self):
        """Test status retrieval for non-existent payment."""
        non_existent_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{non_existent_id}/status", headers=headers)
        
        # Should return 404 Not Found
        assert response.status_code == 404
        
        # Validate error response schema
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert "timestamp" in data

    def test_get_payment_status_invalid_uuid(self):
        """Test status retrieval with invalid UUID format."""
        invalid_id = "invalid-uuid-format"
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{invalid_id}/status", headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_get_payment_status_unauthorized(self):
        """Test payment status retrieval without authorization."""
        payment_id = str(uuid4())
        
        response = client.get(f"/api/v1/payments/{payment_id}/status")
        
        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_get_payment_status_invalid_token(self):
        """Test payment status retrieval with invalid JWT token."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer invalid-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}/status", headers=headers)
        
        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_get_payment_status_forbidden_access(self):
        """Test access to payment status belonging to different user."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token-different-user"}
        
        response = client.get(f"/api/v1/payments/{payment_id}/status", headers=headers)
        
        # Should return 404 Not Found (not 403 to avoid information disclosure)
        assert response.status_code == 404

    def test_get_payment_status_pending(self):
        """Test status retrieval for pending payment."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}/status", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Status should be valid
        if data["status"] == "PENDING":
            # Pending payments should have recent updated_at
            assert "updated_at" in data

    def test_get_payment_status_processing(self):
        """Test status retrieval for processing payment."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}/status", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Status should be valid
        if data["status"] == "PROCESSING":
            # Processing payments should have updated timestamp
            assert "updated_at" in data

    def test_get_payment_status_completed(self):
        """Test status retrieval for completed payment."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}/status", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Status should be valid
        if data["status"] == "COMPLETED":
            # Completed payments should have final timestamp
            assert "updated_at" in data

    def test_get_payment_status_failed(self):
        """Test status retrieval for failed payment."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}/status", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Status should be valid
        if data["status"] == "FAILED":
            # Failed payments should have failure timestamp
            assert "updated_at" in data

    def test_get_payment_status_timestamp_format(self):
        """Test that updated_at timestamp is in correct ISO format."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}/status", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Validate timestamp format (ISO 8601)
        import datetime
        
        try:
            datetime.datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("updated_at is not in valid ISO format")

    def test_get_payment_status_minimal_response(self):
        """Test that response contains only necessary fields."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}/status", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Should contain exactly the expected fields
        expected_fields = {"payment_id", "status", "updated_at"}
        actual_fields = set(data.keys())
        
        # All expected fields should be present
        assert expected_fields.issubset(actual_fields)
        
        # No unexpected fields should be present (this is a lightweight endpoint)
        unexpected_fields = actual_fields - expected_fields
        assert len(unexpected_fields) == 0, f"Unexpected fields: {unexpected_fields}"

    def test_get_payment_status_multiple_requests_consistency(self):
        """Test that multiple status requests return consistent data."""
        payment_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Make first request
        response1 = client.get(f"/api/v1/payments/{payment_id}/status", headers=headers)
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Make second request immediately
        response2 = client.get(f"/api/v1/payments/{payment_id}/status", headers=headers)
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Payment ID should be consistent
        assert data1["payment_id"] == data2["payment_id"]
        
        # Status should be consistent (unless payment is actively processing)
        # This test documents expected behavior for status consistency

    def test_get_payment_status_case_sensitivity(self):
        """Test that payment ID is case sensitive."""
        payment_id = str(uuid4()).upper()  # Use uppercase UUID
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get(f"/api/v1/payments/{payment_id}/status", headers=headers)
        
        # Should handle case appropriately (UUIDs are typically case-insensitive)
        # This test documents the expected behavior
        assert response.status_code in [200, 400, 404]
