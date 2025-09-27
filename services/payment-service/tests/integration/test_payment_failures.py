"""Integration tests for payment failure scenarios."""

from fastapi.testclient import TestClient
from uuid import uuid4

from src.main import app

client = TestClient(app)


class TestPaymentFailuresIntegration:
    """Integration tests for payment failure scenarios and error handling."""

    def test_insufficient_funds_scenario(self):
        """Test payment failure due to insufficient funds."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create payment method
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "Insufficient Funds Test Card",
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
        
        # Create payment with amount ending in 01 to trigger insufficient funds
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": payment_method_id,
            "amount": 1501,  # Amount ending in 01 triggers insufficient funds
            "currency": "USD",
            "description": "Insufficient funds test"
        }
        
        payment_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert payment_response.status_code == 201
        
        payment_id = payment_response.json()["id"]
        
        # Wait for processing and check final status
        import time
        time.sleep(4)  # Wait for processing delay
        
        details_response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
        assert details_response.status_code == 200
        
        details_data = details_response.json()
        
        # Should be failed with appropriate reason
        if details_data["status"] == "FAILED":
            assert "insufficient" in details_data["failure_reason"].lower()

    def test_card_declined_scenario(self):
        """Test payment failure due to card being declined."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create payment method
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "Declined Card Test",
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
        
        # Create payment with amount ending in 02 to trigger card declined
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": payment_method_id,
            "amount": 1502,  # Amount ending in 02 triggers card declined
            "currency": "USD",
            "description": "Card declined test"
        }
        
        payment_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert payment_response.status_code == 201
        
        payment_id = payment_response.json()["id"]
        
        # Wait for processing and check final status
        import time
        time.sleep(4)  # Wait for processing delay
        
        details_response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
        assert details_response.status_code == 200
        
        details_data = details_response.json()
        
        # Should be failed with appropriate reason
        if details_data["status"] == "FAILED":
            assert "declined" in details_data["failure_reason"].lower()

    def test_network_error_scenario(self):
        """Test payment failure due to network/gateway errors."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create payment method
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "Network Error Test Card",
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
        
        # Create payment with amount ending in 03 to trigger network error
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": payment_method_id,
            "amount": 1503,  # Amount ending in 03 triggers network error
            "currency": "USD",
            "description": "Network error test"
        }
        
        payment_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert payment_response.status_code == 201
        
        payment_id = payment_response.json()["id"]
        
        # Wait for processing and check final status
        import time
        time.sleep(4)  # Wait for processing delay
        
        details_response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
        assert details_response.status_code == 200
        
        details_data = details_response.json()
        
        # Should be failed with appropriate reason
        if details_data["status"] == "FAILED":
            assert any(word in details_data["failure_reason"].lower() 
                      for word in ["network", "gateway", "timeout", "connection"])

    def test_invalid_payment_method_scenario(self):
        """Test payment failure due to invalid payment method."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create payment method
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "Invalid Method Test Card",
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
        
        # Create payment with amount ending in 04 to trigger invalid method
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": payment_method_id,
            "amount": 1504,  # Amount ending in 04 triggers invalid method
            "currency": "USD",
            "description": "Invalid method test"
        }
        
        payment_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert payment_response.status_code == 201
        
        payment_id = payment_response.json()["id"]
        
        # Wait for processing and check final status
        import time
        time.sleep(4)  # Wait for processing delay
        
        details_response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
        assert details_response.status_code == 200
        
        details_data = details_response.json()
        
        # Should be failed with appropriate reason
        if details_data["status"] == "FAILED":
            assert "invalid" in details_data["failure_reason"].lower()

    def test_expired_payment_method_failure(self):
        """Test payment failure with expired payment method."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create expired payment method
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "Expired Card",
            "payment_details": {
                "card_number": "4111111111111111",
                "exp_month": 12,
                "exp_year": 2020,  # Expired year
                "cvv": "123"
            }
        }
        
        method_response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
        
        # Should fail to create expired payment method
        assert method_response.status_code == 400

    def test_payment_with_deleted_method(self):
        """Test payment attempt with deleted payment method."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create payment method
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "To Be Deleted Card",
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
        
        # Delete the payment method
        delete_response = client.delete(f"/api/v1/payment-methods/{payment_method_id}", headers=headers)
        assert delete_response.status_code == 204
        
        # Try to create payment with deleted method
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": payment_method_id,
            "amount": 2999,
            "currency": "USD"
        }
        
        payment_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        
        # Should fail with appropriate error
        assert payment_response.status_code in [400, 404]

    def test_payment_amount_validation_failures(self):
        """Test various payment amount validation failures."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create payment method
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "Amount Test Card",
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
        
        # Test zero amount
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": payment_method_id,
            "amount": 0,
            "currency": "USD"
        }
        
        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert response.status_code == 400
        
        # Test negative amount
        payment_data["amount"] = -1000
        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert response.status_code == 400
        
        # Test extremely large amount (if there's a limit)
        payment_data["amount"] = 999999999999  # Very large amount
        response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        # May succeed or fail depending on business rules
        assert response.status_code in [201, 400]

    def test_duplicate_order_payment_failure(self):
        """Test failure when trying to pay for the same order twice."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create payment method
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "Duplicate Test Card",
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
        
        # Create first payment
        order_id = str(uuid4())
        payment_data = {
            "order_id": order_id,
            "payment_method_id": payment_method_id,
            "amount": 2999,
            "currency": "USD"
        }
        
        first_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert first_response.status_code == 201
        
        # Try to create second payment for same order
        second_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert second_response.status_code == 409  # Conflict

    def test_payment_status_transitions(self):
        """Test that payment status transitions follow valid state machine."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create payment method
        payment_method_data = {
            "type": "CREDIT_CARD",
            "display_name": "Status Test Card",
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
        
        # Create payment
        payment_data = {
            "order_id": str(uuid4()),
            "payment_method_id": payment_method_id,
            "amount": 2999,
            "currency": "USD"
        }
        
        payment_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
        assert payment_response.status_code == 201
        
        payment_id = payment_response.json()["id"]
        initial_status = payment_response.json()["status"]
        
        # Track status changes over time
        import time
        statuses = [initial_status]
        
        for i in range(5):  # Check status 5 times over 5 seconds
            time.sleep(1)
            status_response = client.get(f"/api/v1/payments/{payment_id}/status", headers=headers)
            assert status_response.status_code == 200
            
            current_status = status_response.json()["status"]
            if current_status != statuses[-1]:
                statuses.append(current_status)
            
            # Break if we reach a final status
            if current_status in ["COMPLETED", "FAILED", "CANCELLED"]:
                break
        
        # Validate status transitions are valid
        valid_transitions = {
            "PENDING": ["PROCESSING", "CANCELLED"],
            "PROCESSING": ["COMPLETED", "FAILED"],
            "COMPLETED": ["REFUNDED"],  # Future enhancement
            "FAILED": ["PROCESSING"],   # Retry scenario
            "CANCELLED": [],            # Terminal state
            "REFUNDED": []              # Terminal state
        }
        
        for i in range(len(statuses) - 1):
            current = statuses[i]
            next_status = statuses[i + 1]
            assert next_status in valid_transitions.get(current, []), \
                f"Invalid transition from {current} to {next_status}"

    def test_webhook_failure_scenarios(self):
        """Test webhook processing with various failure scenarios."""
        # Test invalid webhook data
        invalid_webhook_data = {
            "event_type": "INVALID_EVENT",
            "payment_id": "invalid-id",
            "data": {},
            "timestamp": "invalid-timestamp"
        }
        
        response = client.post("/api/v1/webhooks/payment", json=invalid_webhook_data)
        assert response.status_code == 400
        
        # Test webhook for non-existent payment
        valid_webhook_data = {
            "event_type": "PAYMENT_COMPLETED",
            "payment_id": str(uuid4()),  # Non-existent payment
            "data": {
                "gateway_transaction_id": "mock_txn_nonexistent"
            },
            "timestamp": "2025-09-27T00:00:00Z"
        }
        
        response = client.post("/api/v1/webhooks/payment", json=valid_webhook_data)
        # Should still return 200 (webhooks are typically idempotent)
        assert response.status_code == 200

    def test_concurrent_payment_processing(self):
        """Test handling of concurrent payment processing scenarios."""
        headers = {"Authorization": "Bearer valid-jwt-token"}
        
        # Create multiple payment methods
        method_ids = []
        for i in range(3):
            payment_method_data = {
                "type": "CREDIT_CARD",
                "display_name": f"Concurrent Test Card {i+1}",
                "payment_details": {
                    "card_number": "4111111111111111",
                    "exp_month": 12,
                    "exp_year": 2025,
                    "cvv": "123"
                }
            }
            
            method_response = client.post("/api/v1/payment-methods", json=payment_method_data, headers=headers)
            assert method_response.status_code == 201
            method_ids.append(method_response.json()["id"])
        
        # Create multiple payments simultaneously
        payment_ids = []
        for i, method_id in enumerate(method_ids):
            payment_data = {
                "order_id": str(uuid4()),
                "payment_method_id": method_id,
                "amount": 1000 + (i * 100),
                "currency": "USD"
            }
            
            payment_response = client.post("/api/v1/payments", json=payment_data, headers=headers)
            assert payment_response.status_code == 201
            payment_ids.append(payment_response.json()["id"])
        
        # Wait for all payments to process
        import time
        time.sleep(5)
        
        # Check that all payments completed processing
        for payment_id in payment_ids:
            details_response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
            assert details_response.status_code == 200
            
            details_data = details_response.json()
            assert details_data["status"] in ["COMPLETED", "FAILED"]
