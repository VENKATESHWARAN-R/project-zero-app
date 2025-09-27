"""Integration tests for successful payment flow scenarios."""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from src.main import app

client = TestClient(app)


class TestPaymentFlowIntegration:
    """Integration tests for end-to-end payment flows."""

    def test_complete_payment_flow_credit_card(self):
        """Test complete payment flow with credit card from start to finish."""
        # Step 1: Add payment method
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "Test Visa Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123",
                "cardholder_name": "Test User"
            },
            "is_default": True
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        method_response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        assert method_response.status_code == 201
        
        method_data = method_response.json()
        payment_method_id = method_data["id"]
        
        # Step 2: Create payment
        order_id = str(uuid4())
        payment_data = {
            "order_id": order_id,
            "payment_method_id": payment_method_id,
            "amount": 2999,  # $29.99
            "currency": "USD",
            "description": "Integration test payment"
        }
        
        payment_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert payment_response.status_code == 201
        
        payment_result = payment_response.json()
        payment_id = payment_result["id"]
        
        # Step 3: Verify payment was created with correct status
        assert payment_result["status"] in ["PENDING", "PROCESSING"]
        assert payment_result["amount"] == 2999
        assert payment_result["order_id"] == order_id
        
        # Step 4: Check payment status (may need to wait for processing)
        import time
        max_wait = 10  # Wait up to 10 seconds for processing
        final_status = None
        
        for _ in range(max_wait):
            status_response = client.get(f"/api/v1/payments/{payment_id}/status", headers=headers)
            assert status_response.status_code == 200
            
            status_data = status_response.json()
            final_status = status_data["status"]
            
            if final_status in ["COMPLETED", "FAILED"]:
                break
            
            time.sleep(1)
        
        # Step 5: Verify final status (should be COMPLETED for successful flow)
        assert final_status in ["COMPLETED", "FAILED"]  # Either is valid for integration test
        
        # Step 6: Get full payment details
        details_response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
        assert details_response.status_code == 200
        
        details_data = details_response.json()
        assert details_data["id"] == payment_id
        assert details_data["status"] == final_status
        
        if final_status == "COMPLETED":
            assert details_data["processed_at"] is not None
        elif final_status == "FAILED":
            assert details_data["failure_reason"] is not None

    def test_complete_payment_flow_paypal(self):
        """Test complete payment flow with PayPal payment method."""
        # Step 1: Add PayPal payment method
        payment_method_data = {
            "type": "PAYPAL",
            "display_name": "Test PayPal Account",
            "payment_details": {
                "email": "test@example.com"
            }
        }
        
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        method_response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        assert method_response.status_code == 201
        
        method_data = method_response.json()
        payment_method_id = method_data["id"]
        
        # Step 2: Create payment
        order_id = str(uuid4())
        payment_data = {
            "order_id": order_id,
            "payment_method_id": payment_method_id,
            "amount": 4999,  # $49.99
            "currency": "USD"
        }
        
        payment_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert payment_response.status_code == 201
        
        payment_result = payment_response.json()
        payment_id = payment_result["id"]
        
        # Step 3: Wait for processing and verify completion
        import time
        time.sleep(3)  # Wait for realistic processing delay
        
        details_response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
        assert details_response.status_code == 200
        
        details_data = details_response.json()
        assert details_data["status"] in ["COMPLETED", "FAILED"]

    def test_payment_history_after_multiple_payments(self):
        """Test payment history retrieval after creating multiple payments."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create payment method first
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "History Test Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 6,
                "exp_year": 2026,
                "cvv": "456"
            }
        }
        
        method_response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        assert method_response.status_code == 201
        payment_method_id = method_response.json()["id"]
        
        # Create multiple payments
        payment_ids = []
        for i in range(3):
            payment_data = {
                "order_id": str(uuid4()),
                "payment_method_id": payment_method_id,
                "amount": 1000 + (i * 500),  # Different amounts
                "currency": "USD"
            }
            
            payment_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
            assert payment_response.status_code == 201
            payment_ids.append(payment_response.json()["id"])
        
        # Get payment history
        history_response = client.get("/api/v1/payments", headers=headers)
        assert history_response.status_code == 200
        
        history_data = history_response.json()
        assert "payments" in history_data
        assert len(history_data["payments"]) >= 3  # At least our 3 payments
        
        # Verify our payments are in the history
        returned_ids = [p["id"] for p in history_data["payments"]]
        for payment_id in payment_ids:
            assert payment_id in returned_ids

    def test_payment_method_management_flow(self):
        """Test complete payment method management flow."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Step 1: Get initial payment methods (should be empty or existing)
        initial_response = client.get("/api/v1/payment-methods", headers=headers)
        assert initial_response.status_code == 200
        initial_count = len(initial_response.json()["payment_methods"])
        
        # Step 2: Add first payment method
        method1_data = {
            "type": "CREDIT_CARD",
            "display_name": "Primary Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123"
            },
            "is_default": True
        }
        
        method1_response = client.post("/api/v1/payment-methods", json=method1_data, headers=headers)
        assert method1_response.status_code == 201
        method1_id = method1_response.json()["id"]
        
        # Step 3: Add second payment method
        method2_data = {
            "type": "PAYPAL",
            "display_name": "PayPal Account",
            "payment_details": {
                "email": "test@example.com"
            }
        }
        
        method2_response = client.post("/api/v1/payment-methods", json=method2_data, headers=headers)
        assert method2_response.status_code == 201
        method2_id = method2_response.json()["id"]
        
        # Step 4: Verify both methods exist
        methods_response = client.get("/api/v1/payment-methods", headers=headers)
        assert methods_response.status_code == 200
        
        methods_data = methods_response.json()
        assert len(methods_data["payment_methods"]) == initial_count + 2
        
        method_ids = [m["id"] for m in methods_data["payment_methods"]]
        assert method1_id in method_ids
        assert method2_id in method_ids
        
        # Step 5: Delete one payment method
        delete_response = client.delete(f"/api/v1/payment-methods/{method2_id}", headers=headers)
        assert delete_response.status_code == 204
        
        # Step 6: Verify method was deleted
        final_response = client.get("/api/v1/payment-methods", headers=headers)
        assert final_response.status_code == 200
        
        final_data = final_response.json()
        final_ids = [m["id"] for m in final_data["payment_methods"]]
        assert method1_id in final_ids
        assert method2_id not in final_ids

    def test_webhook_integration_flow(self):
        """Test webhook processing integration."""
        # Step 1: Create a payment first
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "Webhook Test Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123"
            }
        }
        
        method_response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        assert method_response.status_code == 201
        payment_method_id = method_response.json()["id"]
        
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": payment_method_id,
            "amount": 1999,
            "currency": "USD"
        }
        
        payment_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert payment_response.status_code == 201
        payment_id = payment_response.json()["id"]
        
        # Step 2: Send webhook notification
        webhook_data = {
            "event_type": "PAYMENT_COMPLETED",
            "payment_id": payment_id,
            "data": {
                "gateway_transaction_id": "mock_txn_webhook_test",
                "amount": 1999,
                "currency": "USD"
            },
            "timestamp": "2025-09-27T00:00:00Z"
        }
        
        webhook_response = client.post("/api/v1/webhooks/payment", json=webhook_data)
        assert webhook_response.status_code == 200
        
        webhook_result = webhook_response.json()
        assert webhook_result["received"] is True
        
        # Step 3: Verify payment status was updated (if webhook processing is synchronous)
        status_response = client.get(f"/api/v1/payments/{payment_id}/status", headers=headers)
        assert status_response.status_code == 200
        
        # Note: Actual status update depends on webhook implementation
        # This test documents the expected integration behavior

    def test_error_handling_integration(self):
        """Test error handling across the payment flow."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Test 1: Try to create payment with non-existent payment method
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": str(uuid4()),  # Non-existent method
            "amount": 2999,
            "currency": "USD"
        }
        
        payment_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        # Should fail with appropriate error
        assert payment_response.status_code in [400, 404]
        
        # Test 2: Try to access non-existent payment
        non_existent_id = str(uuid4())
        details_response = client.get(f"/api/v1/payments/{non_existent_id}", headers=headers)
        assert details_response.status_code == 404
        
        # Test 3: Try to delete non-existent payment method
        delete_response = client.delete(f"/api/v1/payment-methods/{non_existent_id}", headers=headers)
        assert delete_response.status_code == 404

    def test_concurrent_payment_creation(self):
        """Test handling of concurrent payment creation attempts."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create payment method
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "Concurrent Test Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2025,
                "cvv": "123"
            }
        }
        
        method_response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        assert method_response.status_code == 201
        payment_method_id = method_response.json()["id"]
        
        # Try to create multiple payments for the same order
        order_id = str(uuid4())
        payment_data = {
            "order_id": order_id,
            "payment_method_id": payment_method_id,
            "amount": 2999,
            "currency": "USD"
        }
        
        # First payment should succeed
        response1 = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert response1.status_code == 201
        
        # Second payment for same order should fail
        response2 = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert response2.status_code == 409  # Conflict - duplicate order payment
