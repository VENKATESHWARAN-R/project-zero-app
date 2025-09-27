"""Contract tests for POST /api/v1/payment-methods endpoint."""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestPaymentMethodsPostContract:
    """Contract tests for payment method creation endpoint."""

    def test_create_credit_card_method_success(self):
        """Test successful creation of credit card payment method."""
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "My Visa Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123",
                "cardholder_name": "John Doe"
            },
            "is_default": True
        }
        
        headers = {
            "Authorization": "Bearer valid-jwt-token",
            "Content-Type": "application/json"
        }
        
        response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        
        # Should return 201 Created
        assert response.status_code == 201
        
        # Validate response schema
        data = response.json()
        assert "id" in data
        assert "user_id" in data
        assert "type" in data
        assert "display_name" in data
        assert "masked_details" in data
        assert "is_default" in data
        assert "is_active" in data
        assert "created_at" in data
        
        # Validate data types and values
        assert isinstance(data["id"], str)
        assert isinstance(data["user_id"], str)
        assert data["type"] == "CREDIT_CARD"
        assert data["display_name"] == payment_method_data["display_name"]
        assert data["is_default"] == payment_method_data["is_default"]
        assert data["is_active"] is True
        
        # Validate masked details structure
        assert isinstance(data["masked_details"], dict)
        assert "last_four" in data["masked_details"]
        assert "brand" in data["masked_details"]
        assert "exp_month" in data["masked_details"]
        assert "exp_year" in data["masked_details"]
        
        # Ensure sensitive data is masked
        assert data["masked_details"]["last_four"] == "1111"
        assert len(data["masked_details"]["last_four"]) == 4

    def test_create_debit_card_method_success(self):
        """Test successful creation of debit card payment method."""
        payment_method_data = {
            "type": "DEBIT_CARD",
            "display_name": "My Debit Card",
            "payment_details": {
                "card_number": "5555555555554444",
                "exp_month": 6,
                "exp_year": 2026,
                "cvv": "456",
                "cardholder_name": "Jane Smith"
            }
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        
        # Should return 201 Created
        assert response.status_code == 201
        
        data = response.json()
        assert data["type"] == "DEBIT_CARD"
        assert data["is_default"] is False  # Default value when not specified

    def test_create_paypal_method_success(self):
        """Test successful creation of PayPal payment method."""
        payment_method_data = {
            "type": "PAYPAL",
            "display_name": "My PayPal Account",
            "payment_details": {
                "email": "user@example.com"
            }
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        
        # Should return 201 Created
        assert response.status_code == 201
        
        data = response.json()
        assert data["type"] == "PAYPAL"
        
        # Validate PayPal masked details
        assert "email" in data["masked_details"]
        assert data["masked_details"]["email"] == "user@example.com"

    def test_create_payment_method_missing_required_fields(self):
        """Test payment method creation with missing required fields."""
        # Missing type
        payment_method_data = {
            "display_name": "My Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123"
            }
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_create_payment_method_invalid_type(self):
        """Test payment method creation with invalid type."""
        payment_method_data = {
            "type": "INVALID_TYPE",
            "display_name": "My Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123"
            }
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_create_payment_method_invalid_card_number(self):
        """Test payment method creation with invalid card number."""
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "My Card",
            "payment_details": {
                "card_number": "invalid-card-number",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123"
            }
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_create_payment_method_invalid_expiry_month(self):
        """Test payment method creation with invalid expiry month."""
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "My Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 13,  # Invalid month
                "exp_year": 2025,
                "cvv": "123"
            }
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_create_payment_method_invalid_expiry_year(self):
        """Test payment method creation with invalid expiry year."""
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "My Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2020,  # Past year
                "cvv": "123"
            }
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_create_payment_method_invalid_cvv(self):
        """Test payment method creation with invalid CVV."""
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "My Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "12"  # Too short
            }
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_create_payment_method_invalid_email(self):
        """Test PayPal payment method creation with invalid email."""
        payment_method_data = {
            "type": "PAYPAL",
            "display_name": "My PayPal",
            "payment_details": {
                "email": "invalid-email"
            }
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_create_payment_method_unauthorized(self):
        """Test payment method creation without authorization."""
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "My Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123"
            }
        }
        
        response = client.post("/api/v1/payment-methods", json=payment_method_data)
        
        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_create_payment_method_invalid_token(self):
        """Test payment method creation with invalid JWT token."""
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "My Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123"
            }
        }
        
        headers = {"Authorization": "Bearer invalid-token"}
        
        response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        
        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_create_payment_method_long_display_name(self):
        """Test payment method creation with display name exceeding max length."""
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "x" * 150,  # Exceeds 100 character limit
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123"
            }
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_create_payment_method_mismatched_details(self):
        """Test payment method creation with mismatched type and details."""
        # PayPal type with credit card details
        payment_method_data = {
            "type": "PAYPAL",
            "display_name": "My PayPal",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123"
            }
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_create_payment_method_expires_at_field(self):
        """Test that expires_at field is set for card payment methods."""
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "My Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123"
            }
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        
        # Should return 201 Created
        assert response.status_code == 201
        
        data = response.json()
        
        # For card methods, expires_at should be present
        if data["type"] in ["CREDIT_CARD", "DEBIT_CARD"]:
            assert "expires_at" in data
            assert data["expires_at"] is not None
