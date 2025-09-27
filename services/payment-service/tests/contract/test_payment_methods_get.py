"""Contract tests for GET /api/v1/payment-methods endpoint."""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestPaymentMethodsGetContract:
    """Contract tests for payment methods retrieval endpoint."""

    def test_get_payment_methods_success(self):
        """Test successful retrieval of user payment methods."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get("/api/v1/payment-methods", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Validate response schema
        data = response.json()
        assert "payment_methods" in data
        assert isinstance(data["payment_methods"], list)

    def test_get_payment_methods_schema_validation(self):
        """Test that payment method objects have correct schema."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get("/api/v1/payment-methods", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Validate each payment method schema
        for method in data["payment_methods"]:
            # Required fields
            assert "id" in method
            assert "user_id" in method
            assert "type" in method
            assert "display_name" in method
            assert "masked_details" in method
            assert "is_default" in method
            assert "is_active" in method
            assert "created_at" in method
            
            # Validate data types
            assert isinstance(method["id"], str)
            assert isinstance(method["user_id"], str)
            assert isinstance(method["type"], str)
            assert isinstance(method["display_name"], str)
            assert isinstance(method["masked_details"], dict)
            assert isinstance(method["is_default"], bool)
            assert isinstance(method["is_active"], bool)
            assert isinstance(method["created_at"], str)
            
            # Validate enum values
            assert method["type"] in ["CREDIT_CARD", "DEBIT_CARD", "PAYPAL"]

    def test_get_payment_methods_unauthorized(self):
        """Test payment methods retrieval without authorization."""
        response = client.get("/api/v1/payment-methods")
        
        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_get_payment_methods_invalid_token(self):
        """Test payment methods retrieval with invalid JWT token."""
        headers = {"Authorization": "Bearer invalid-token"}
        
        response = client.get("/api/v1/payment-methods", headers=headers)
        
        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_get_payment_methods_empty_result(self):
        """Test payment methods retrieval when user has no methods."""
        headers = {"Authorization": "Bearer valid-jwt-token-no-methods"}
        
        response = client.get("/api/v1/payment-methods", headers=headers)
        
        # Should return 200 OK with empty list
        assert response.status_code == 200
        
        data = response.json()
        assert data["payment_methods"] == []

    def test_get_payment_methods_masked_details_credit_card(self):
        """Test that credit card details are properly masked."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get("/api/v1/payment-methods", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Find credit card methods and validate masking
        for method in data["payment_methods"]:
            if method["type"] == "CREDIT_CARD":
                masked = method["masked_details"]
                assert "last_four" in masked
                assert "brand" in masked
                assert "exp_month" in masked
                assert "exp_year" in masked
                
                # Validate masking
                assert len(masked["last_four"]) == 4
                assert masked["last_four"].isdigit()

    def test_get_payment_methods_masked_details_paypal(self):
        """Test that PayPal details are properly handled."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get("/api/v1/payment-methods", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Find PayPal methods and validate details
        for method in data["payment_methods"]:
            if method["type"] == "PAYPAL":
                masked = method["masked_details"]
                assert "email" in masked
                assert "@" in masked["email"]  # Should contain email format

    def test_get_payment_methods_default_method_logic(self):
        """Test that only one method can be default per user."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get("/api/v1/payment-methods", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Count default methods
        default_count = sum(1 for method in data["payment_methods"] if method["is_default"])
        
        # Should have at most one default method
        assert default_count <= 1

    def test_get_payment_methods_active_status(self):
        """Test that active status is properly returned."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get("/api/v1/payment-methods", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # All returned methods should have is_active field
        for method in data["payment_methods"]:
            assert "is_active" in method
            assert isinstance(method["is_active"], bool)

    def test_get_payment_methods_expires_at_field(self):
        """Test that expires_at field is present for card methods."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get("/api/v1/payment-methods", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Card methods should have expires_at field
        for method in data["payment_methods"]:
            if method["type"] in ["CREDIT_CARD", "DEBIT_CARD"]:
                assert "expires_at" in method
                # Can be null or a valid timestamp
                if method["expires_at"] is not None:
                    assert isinstance(method["expires_at"], str)

    def test_get_payment_methods_timestamp_format(self):
        """Test that timestamps are in correct ISO format."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.get("/api/v1/payment-methods", headers=headers)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Validate timestamp formats
        import datetime
        
        for method in data["payment_methods"]:
            # created_at should be valid ISO format
            try:
                datetime.datetime.fromisoformat(method["created_at"].replace('Z', '+00:00'))
            except ValueError:
                pytest.fail("created_at is not in valid ISO format")
            
            # expires_at should be valid ISO format if present
            if method.get("expires_at"):
                try:
                    datetime.datetime.fromisoformat(method["expires_at"].replace('Z', '+00:00'))
                except ValueError:
                    pytest.fail("expires_at is not in valid ISO format")

    def test_get_payment_methods_ordering(self):
        """Test that payment methods are returned in consistent order."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Make multiple requests
        response1 = client.get("/api/v1/payment-methods", headers=headers)
        response2 = client.get("/api/v1/payment-methods", headers=headers)
        
        # Both should return 200 OK
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Order should be consistent
        if len(data1["payment_methods"]) > 1:
            ids1 = [method["id"] for method in data1["payment_methods"]]
            ids2 = [method["id"] for method in data2["payment_methods"]]
            assert ids1 == ids2
