"""Integration tests for payment method management."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestPaymentMethodsIntegration:
    """Integration tests for payment method management flows."""

    def test_payment_method_lifecycle(self):
        """Test complete payment method lifecycle from creation to deletion."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Step 1: Create credit card payment method
        credit_card_data = {
            "type": "CREDIT_CARD",
            "display_name": "My Primary Visa",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123",
                "cardholder_name": "John Doe"
            },
            "is_default": True
        }
        
        create_response = client.post("/api/v1/payment-methods", json=credit_card_data, headers=headers)
        assert create_response.status_code == 201
        
        method_data = create_response.json()
        method_id = method_data["id"]
        
        # Verify creation response
        assert method_data["type"] == "CREDIT_CARD"
        assert method_data["display_name"] == "My Primary Visa"
        assert method_data["is_default"] is True
        assert method_data["is_active"] is True
        
        # Verify sensitive data is masked
        assert "last_four" in method_data["masked_details"]
        assert method_data["masked_details"]["last_four"] == "1111"
        
        # Step 2: Retrieve all payment methods
        list_response = client.get("/api/v1/payment-methods", headers=headers)
        assert list_response.status_code == 200
        
        methods_list = list_response.json()["payment_methods"]
        created_method = next((m for m in methods_list if m["id"] == method_id), None)
        assert created_method is not None
        assert created_method["display_name"] == "My Primary Visa"
        
        # Step 3: Use payment method for a payment
        from uuid import uuid4
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": method_id,
            "amount": 2999,
            "currency": "USD"
        }
        
        payment_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert payment_response.status_code == 201
        
        # Step 4: Try to delete payment method (should succeed or handle gracefully)
        delete_response = client.delete(f"/api/v1/payment-methods/{method_id}", headers=headers)
        assert delete_response.status_code in [204, 400]  # May prevent deletion if used in payments
        
        # Step 5: Verify deletion (if successful)
        if delete_response.status_code == 204:
            final_list_response = client.get("/api/v1/payment-methods", headers=headers)
            assert final_list_response.status_code == 200
            
            final_methods = final_list_response.json()["payment_methods"]
            deleted_method = next((m for m in final_methods if m["id"] == method_id), None)
            assert deleted_method is None

    def test_multiple_payment_methods_management(self):
        """Test managing multiple payment methods with different types."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create multiple payment methods
        methods_data = [
            {
                "type": "CREDIT_CARD",
                "display_name": "Visa Card",
                "payment_details": {
                    "card_number": "4111111111111111",
                    "exp_month": 12,
                    "exp_year": 2025,
                    "cvv": "123"
                },
                "is_default": True
            },
            {
                "type": "DEBIT_CARD",
                "display_name": "Debit Card",
                "payment_details": {
                    "card_number": "5555555555554444",
                    "exp_month": 6,
                    "exp_year": 2026,
                    "cvv": "456"
                }
            },
            {
                "type": "PAYPAL",
                "display_name": "PayPal Account",
                "payment_details": {
                    "email": "user@example.com"
                }
            }
        ]
        
        created_methods = []
        
        # Create all methods
        for method_data in methods_data:
            response = client.post("/api/v1/payment-methods", json=method_data, headers=headers)
            assert response.status_code == 201
            created_methods.append(response.json())
        
        # Verify all methods exist
        list_response = client.get("/api/v1/payment-methods", headers=headers)
        assert list_response.status_code == 200
        
        methods_list = list_response.json()["payment_methods"]
        assert len(methods_list) >= 3
        
        # Verify each method type
        method_types = [m["type"] for m in methods_list]
        assert "CREDIT_CARD" in method_types
        assert "DEBIT_CARD" in method_types
        assert "PAYPAL" in method_types
        
        # Verify only one default method
        default_methods = [m for m in methods_list if m["is_default"]]
        assert len(default_methods) <= 1
        
        # Test using each method for payments
        from uuid import uuid4
        for method in created_methods:
            payment_data = {
                "order_id": str(uuid4()),
                "payment_method_id": method["id"],
                "amount": 1999,
                "currency": "USD"
            }
            
            payment_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
            assert payment_response.status_code == 201

    def test_payment_method_validation_edge_cases(self):
        """Test payment method validation with various edge cases."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Test card expiring this month
        import datetime
        current_date = datetime.datetime.now()
        
        expiring_card_data = {
            "type": "CREDIT_CARD",
            "display_name": "Expiring Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": current_date.month,
                "exp_year": current_date.year,
                "cvv": "123"
            }
        }
        
        response = client.post("/api/v1/payment-methods", json=expiring_card_data, headers=headers)
        # Should succeed (card expires at end of month)
        assert response.status_code in [201, 400]
        
        # Test various card number formats
        card_numbers = [
            "4111111111111111",  # Visa
            "5555555555554444",  # Mastercard
            "378282246310005",   # American Express
            "6011111111111117"   # Discover
        ]
        
        for i, card_number in enumerate(card_numbers):
            card_data = {
                "type": "CREDIT_CARD",
                "display_name": f"Test Card {i+1}",
                "payment_details": {
                    "card_number": card_number,
                    "exp_month": 12,
                    "exp_year": 2025,
                    "cvv": "123"
                }
            }
            
            response = client.post("/api/v1/payment-methods", json=card_data, headers=headers)
            assert response.status_code == 201
            
            # Verify card brand detection (if implemented)
            method_data = response.json()
            masked_details = method_data["masked_details"]
            assert "brand" in masked_details

    def test_payment_method_security_masking(self):
        """Test that sensitive payment method data is properly masked."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create credit card with sensitive data
        card_data = {
            "type": "CREDIT_CARD",
            "display_name": "Security Test Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123",
                "cardholder_name": "John Doe"
            }
        }
        
        create_response = client.post("/api/v1/payment-methods", json=card_data, headers=headers)
        assert create_response.status_code == 201
        
        method_data = create_response.json()
        
        # Verify sensitive data is not in response
        response_str = str(method_data)
        assert "4111111111111111" not in response_str  # Full card number
        assert "123" not in response_str  # CVV
        
        # Verify masked details are present
        masked_details = method_data["masked_details"]
        assert masked_details["last_four"] == "1111"
        assert "brand" in masked_details
        assert "exp_month" in masked_details
        assert "exp_year" in masked_details
        
        # Verify when retrieving method list
        list_response = client.get("/api/v1/payment-methods", headers=headers)
        assert list_response.status_code == 200
        
        methods_list = list_response.json()["payment_methods"]
        created_method = next((m for m in methods_list if m["id"] == method_data["id"]), None)
        
        # Same masking should apply
        list_response_str = str(created_method)
        assert "4111111111111111" not in list_response_str
        assert "123" not in list_response_str

    def test_payment_method_default_logic(self):
        """Test payment method default assignment logic."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create first method as default
        first_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "First Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123"
            },
            "is_default": True
        }
        
        first_response = client.post("/api/v1/payment-methods", json=first_method_data, headers=headers)
        assert first_response.status_code == 201
        first_method = first_response.json()
        assert first_method["is_default"] is True
        
        # Create second method as default (should replace first as default)
        second_method_data = {
            "type": "PAYPAL",
            "display_name": "PayPal Account",
            "payment_details": {
                "email": "user@example.com"
            },
            "is_default": True
        }
        
        second_response = client.post("/api/v1/payment-methods", json=second_method_data, headers=headers)
        assert second_response.status_code == 201
        second_method = second_response.json()
        assert second_method["is_default"] is True
        
        # Verify only one method is default
        list_response = client.get("/api/v1/payment-methods", headers=headers)
        assert list_response.status_code == 200
        
        methods_list = list_response.json()["payment_methods"]
        default_methods = [m for m in methods_list if m["is_default"]]
        assert len(default_methods) == 1
        assert default_methods[0]["id"] == second_method["id"]

    def test_payment_method_expiration_handling(self):
        """Test handling of payment method expiration."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create card that expires soon
        import datetime
        next_month = datetime.datetime.now() + datetime.timedelta(days=32)
        
        card_data = {
            "type": "CREDIT_CARD",
            "display_name": "Soon to Expire Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": next_month.month,
                "exp_year": next_month.year,
                "cvv": "123"
            }
        }
        
        create_response = client.post("/api/v1/payment-methods", json=card_data, headers=headers)
        assert create_response.status_code == 201
        
        method_data = create_response.json()
        
        # Verify expires_at field is set
        assert "expires_at" in method_data
        assert method_data["expires_at"] is not None
        
        # Verify expiration date calculation
        expires_at = datetime.datetime.fromisoformat(
            method_data["expires_at"].replace('Z', '+00:00')
        ).replace(tzinfo=None)
        
        # Should expire at end of the specified month
        expected_expiry = datetime.datetime(next_month.year, next_month.month, 1)
        # Add one month and subtract one day to get end of month
        if expected_expiry.month == 12:
            expected_expiry = expected_expiry.replace(year=expected_expiry.year + 1, month=1)
        else:
            expected_expiry = expected_expiry.replace(month=expected_expiry.month + 1)
        expected_expiry = expected_expiry - datetime.timedelta(days=1)
        
        # Should be close to expected expiry (within a day)
        assert abs((expires_at.date() - expected_expiry.date()).days) <= 1

    def test_payment_method_concurrent_operations(self):
        """Test concurrent payment method operations."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create method
        method_data = {
            "type": "CREDIT_CARD",
            "display_name": "Concurrent Test Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123"
            }
        }
        
        create_response = client.post("/api/v1/payment-methods", json=method_data, headers=headers)
        assert create_response.status_code == 201
        method_id = create_response.json()["id"]
        
        # Simulate concurrent operations
        # In a real test, these would be actual concurrent requests
        
        # Multiple retrievals should be consistent
        responses = []
        for _ in range(3):
            list_response = client.get("/api/v1/payment-methods", headers=headers)
            assert list_response.status_code == 200
            responses.append(list_response.json())
        
        # All responses should contain the same method
        for response in responses:
            method_ids = [m["id"] for m in response["payment_methods"]]
            assert method_id in method_ids
        
        # Concurrent deletion attempts (second should fail)
        delete_response1 = client.delete(f"/api/v1/payment-methods/{method_id}", headers=headers)
        delete_response2 = client.delete(f"/api/v1/payment-methods/{method_id}", headers=headers)
        
        # First should succeed, second should fail
        assert delete_response1.status_code == 204
        assert delete_response2.status_code == 404
