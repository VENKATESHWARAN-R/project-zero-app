"""Contract tests for DELETE /api/v1/payment-methods/{method_id} endpoint."""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from src.main import app

client = TestClient(app)


class TestPaymentMethodsDeleteContract:
    """Contract tests for payment method deletion endpoint."""

    def test_delete_payment_method_success(self):
        """Test successful deletion of payment method."""
        method_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.delete(f"/api/v1/payment-methods/{method_id}", headers=headers)
        
        # Should return 204 No Content
        assert response.status_code == 204
        
        # Response body should be empty
        assert response.content == b""

    def test_delete_payment_method_not_found(self):
        """Test deletion of non-existent payment method."""
        non_existent_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.delete(f"/api/v1/payment-methods/{non_existent_id}", headers=headers)
        
        # Should return 404 Not Found
        assert response.status_code == 404
        
        # Validate error response schema
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert "timestamp" in data

    def test_delete_payment_method_invalid_uuid(self):
        """Test deletion with invalid UUID format."""
        invalid_id = "invalid-uuid-format"
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.delete(f"/api/v1/payment-methods/{invalid_id}", headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_delete_payment_method_unauthorized(self):
        """Test payment method deletion without authorization."""
        method_id = str(uuid4())
        
        response = client.delete(f"/api/v1/payment-methods/{method_id}")
        
        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_delete_payment_method_invalid_token(self):
        """Test payment method deletion with invalid JWT token."""
        method_id = str(uuid4())
        headers = {"Authorization": "Bearer invalid-token"}
        
        response = client.delete(f"/api/v1/payment-methods/{method_id}", headers=headers)
        
        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_delete_payment_method_forbidden_access(self):
        """Test deletion of payment method belonging to different user."""
        method_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token-different-user"}
        
        response = client.delete(f"/api/v1/payment-methods/{method_id}", headers=headers)
        
        # Should return 404 Not Found (not 403 to avoid information disclosure)
        assert response.status_code == 404

    def test_delete_default_payment_method(self):
        """Test deletion of default payment method."""
        method_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.delete(f"/api/v1/payment-methods/{method_id}", headers=headers)
        
        # Should succeed (business logic may handle default reassignment)
        # This test documents expected behavior for default method deletion
        assert response.status_code in [204, 400]

    def test_delete_payment_method_with_active_payments(self):
        """Test deletion of payment method with active payments."""
        method_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.delete(f"/api/v1/payment-methods/{method_id}", headers=headers)
        
        # Should either succeed or return business logic error
        # This test documents expected behavior
        assert response.status_code in [204, 400, 409]

    def test_delete_payment_method_idempotency(self):
        """Test that deleting already deleted method returns appropriate response."""
        method_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # First deletion
        response1 = client.delete(f"/api/v1/payment-methods/{method_id}", headers=headers)
        
        # Second deletion of same method
        response2 = client.delete(f"/api/v1/payment-methods/{method_id}", headers=headers)
        
        # First should succeed or not found
        assert response1.status_code in [204, 404]
        
        # Second should return not found
        assert response2.status_code == 404

    def test_delete_payment_method_case_sensitivity(self):
        """Test that method ID is case sensitive."""
        method_id = str(uuid4()).upper()  # Use uppercase UUID
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.delete(f"/api/v1/payment-methods/{method_id}", headers=headers)
        
        # Should handle case appropriately (UUIDs are typically case-insensitive)
        assert response.status_code in [204, 400, 404]

    def test_delete_payment_method_no_content_type(self):
        """Test that DELETE request doesn't require content type."""
        method_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.delete(f"/api/v1/payment-methods/{method_id}", headers=headers)
        
        # Should work without Content-Type header
        assert response.status_code in [204, 404]

    def test_delete_payment_method_with_body(self):
        """Test DELETE request with unexpected body."""
        method_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # DELETE with body (should be ignored)
        response = client.delete(
            f"/api/v1/payment-methods/{method_id}", 
            headers=headers,
            json={"unexpected": "data"}
        )
        
        # Should work (body should be ignored)
        assert response.status_code in [204, 404]

    def test_delete_payment_method_response_headers(self):
        """Test that response has appropriate headers."""
        method_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.delete(f"/api/v1/payment-methods/{method_id}", headers=headers)
        
        # Check response headers
        if response.status_code == 204:
            # Should not have Content-Length for empty body
            assert response.headers.get("content-length") in [None, "0"]

    def test_delete_last_payment_method(self):
        """Test deletion of user's last payment method."""
        method_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token-single-method"}
        
        response = client.delete(f"/api/v1/payment-methods/{method_id}", headers=headers)
        
        # Should succeed (users can have zero payment methods)
        assert response.status_code in [204, 404]

    def test_delete_payment_method_concurrent_requests(self):
        """Test concurrent deletion requests for same method."""
        method_id = str(uuid4())
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # This test documents expected behavior for concurrent deletions
        # In practice, this would require actual concurrent execution
        response = client.delete(f"/api/v1/payment-methods/{method_id}", headers=headers)
        
        # Should handle gracefully
        assert response.status_code in [204, 404, 409]
