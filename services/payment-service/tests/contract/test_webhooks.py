"""Contract tests for POST /api/v1/webhooks/payment endpoint."""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from src.main import app

client = TestClient(app)


class TestWebhooksContract:
    """Contract tests for payment webhook endpoint."""

    def test_webhook_payment_initiated_success(self):
        """Test successful processing of payment initiated webhook."""
        webhook_data = {
            "event_type": "PAYMENT_INITIATED",
            "payment_id": str(uuid4()),
            "data": {
                "gateway_transaction_id": "mock_txn_123",
                "amount": 2999,
                "currency": "USD"
            },
            "timestamp": "2025-09-27T00:00:00Z"
        }
        
        # Note: Webhook endpoint should not require authentication
        response = client.post("/api/v1/webhooks/payment", json=webhook_data)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Validate response schema
        data = response.json()
        assert "received" in data
        assert "processed_at" in data
        
        # Validate data types and values
        assert isinstance(data["received"], bool)
        assert data["received"] is True
        assert isinstance(data["processed_at"], str)

    def test_webhook_payment_completed_success(self):
        """Test successful processing of payment completed webhook."""
        webhook_data = {
            "event_type": "PAYMENT_COMPLETED",
            "payment_id": str(uuid4()),
            "data": {
                "gateway_transaction_id": "mock_txn_456",
                "amount": 5999,
                "currency": "USD",
                "completion_time": "2025-09-27T00:05:00Z"
            },
            "timestamp": "2025-09-27T00:05:00Z"
        }
        
        response = client.post("/api/v1/webhooks/payment", json=webhook_data)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        assert data["received"] is True

    def test_webhook_payment_failed_success(self):
        """Test successful processing of payment failed webhook."""
        webhook_data = {
            "event_type": "PAYMENT_FAILED",
            "payment_id": str(uuid4()),
            "data": {
                "gateway_transaction_id": "mock_txn_789",
                "amount": 1999,
                "currency": "USD",
                "failure_reason": "Insufficient funds",
                "failure_code": "INSUFFICIENT_FUNDS"
            },
            "timestamp": "2025-09-27T00:03:00Z"
        }
        
        response = client.post("/api/v1/webhooks/payment", json=webhook_data)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        assert data["received"] is True

    def test_webhook_payment_cancelled_success(self):
        """Test successful processing of payment cancelled webhook."""
        webhook_data = {
            "event_type": "PAYMENT_CANCELLED",
            "payment_id": str(uuid4()),
            "data": {
                "gateway_transaction_id": "mock_txn_101",
                "amount": 3999,
                "currency": "USD",
                "cancellation_reason": "User requested cancellation"
            },
            "timestamp": "2025-09-27T00:02:00Z"
        }
        
        response = client.post("/api/v1/webhooks/payment", json=webhook_data)
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        assert data["received"] is True

    def test_webhook_missing_required_fields(self):
        """Test webhook processing with missing required fields."""
        # Missing event_type
        webhook_data = {
            "payment_id": str(uuid4()),
            "data": {
                "gateway_transaction_id": "mock_txn_123"
            },
            "timestamp": "2025-09-27T00:00:00Z"
        }
        
        response = client.post("/api/v1/webhooks/payment", json=webhook_data)
        
        # Should return 400 Bad Request
        assert response.status_code == 400
        
        # Validate error response schema
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert "timestamp" in data

    def test_webhook_invalid_event_type(self):
        """Test webhook processing with invalid event type."""
        webhook_data = {
            "event_type": "INVALID_EVENT",
            "payment_id": str(uuid4()),
            "data": {
                "gateway_transaction_id": "mock_txn_123"
            },
            "timestamp": "2025-09-27T00:00:00Z"
        }
        
        response = client.post("/api/v1/webhooks/payment", json=webhook_data)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_webhook_invalid_payment_id(self):
        """Test webhook processing with invalid payment ID format."""
        webhook_data = {
            "event_type": "PAYMENT_COMPLETED",
            "payment_id": "invalid-uuid-format",
            "data": {
                "gateway_transaction_id": "mock_txn_123"
            },
            "timestamp": "2025-09-27T00:00:00Z"
        }
        
        response = client.post("/api/v1/webhooks/payment", json=webhook_data)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_webhook_missing_data_field(self):
        """Test webhook processing with missing data field."""
        webhook_data = {
            "event_type": "PAYMENT_COMPLETED",
            "payment_id": str(uuid4()),
            "timestamp": "2025-09-27T00:00:00Z"
        }
        
        response = client.post("/api/v1/webhooks/payment", json=webhook_data)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_webhook_invalid_timestamp_format(self):
        """Test webhook processing with invalid timestamp format."""
        webhook_data = {
            "event_type": "PAYMENT_COMPLETED",
            "payment_id": str(uuid4()),
            "data": {
                "gateway_transaction_id": "mock_txn_123"
            },
            "timestamp": "invalid-timestamp"
        }
        
        response = client.post("/api/v1/webhooks/payment", json=webhook_data)
        
        # Should return 400 Bad Request
        assert response.status_code == 400

    def test_webhook_no_authentication_required(self):
        """Test that webhook endpoint doesn't require authentication."""
        webhook_data = {
            "event_type": "PAYMENT_COMPLETED",
            "payment_id": str(uuid4()),
            "data": {
                "gateway_transaction_id": "mock_txn_123"
            },
            "timestamp": "2025-09-27T00:00:00Z"
        }
        
        # No Authorization header
        response = client.post("/api/v1/webhooks/payment", json=webhook_data)
        
        # Should return 200 OK (webhooks typically don't require auth)
        assert response.status_code == 200

    def test_webhook_content_type_validation(self):
        """Test webhook processing with invalid content type."""
        webhook_data = {
            "event_type": "PAYMENT_COMPLETED",
            "payment_id": str(uuid4()),
            "data": {
                "gateway_transaction_id": "mock_txn_123"
            },
            "timestamp": "2025-09-27T00:00:00Z"
        }
        
        headers = {"Content-Type": "text/plain"}
        
        response = client.post("/api/v1/webhooks/payment", json=webhook_data, headers=headers)
        
        # Should return 400 Bad Request or 415 Unsupported Media Type
        assert response.status_code in [400, 415]

    def test_webhook_large_payload(self):
        """Test webhook processing with large payload."""
        webhook_data = {
            "event_type": "PAYMENT_COMPLETED",
            "payment_id": str(uuid4()),
            "data": {
                "gateway_transaction_id": "mock_txn_123",
                "large_field": "x" * 10000  # Large data field
            },
            "timestamp": "2025-09-27T00:00:00Z"
        }
        
        response = client.post("/api/v1/webhooks/payment", json=webhook_data)
        
        # Should handle large payloads appropriately
        assert response.status_code in [200, 400, 413]  # 413 = Payload Too Large

    def test_webhook_duplicate_processing(self):
        """Test webhook processing with duplicate events."""
        webhook_data = {
            "event_type": "PAYMENT_COMPLETED",
            "payment_id": str(uuid4()),
            "data": {
                "gateway_transaction_id": "mock_txn_duplicate"
            },
            "timestamp": "2025-09-27T00:00:00Z"
        }
        
        # Send same webhook twice
        response1 = client.post("/api/v1/webhooks/payment", json=webhook_data)
        response2 = client.post("/api/v1/webhooks/payment", json=webhook_data)
        
        # Both should succeed (idempotent processing)
        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_webhook_response_time(self):
        """Test that webhook processing is reasonably fast."""
        webhook_data = {
            "event_type": "PAYMENT_COMPLETED",
            "payment_id": str(uuid4()),
            "data": {
                "gateway_transaction_id": "mock_txn_speed_test"
            },
            "timestamp": "2025-09-27T00:00:00Z"
        }
        
        import time
        start_time = time.time()
        
        response = client.post("/api/v1/webhooks/payment", json=webhook_data)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Should respond within reasonable time (5 seconds for webhook processing)
        assert response_time < 5.0

    def test_webhook_processed_at_timestamp(self):
        """Test that processed_at timestamp is valid and recent."""
        webhook_data = {
            "event_type": "PAYMENT_COMPLETED",
            "payment_id": str(uuid4()),
            "data": {
                "gateway_transaction_id": "mock_txn_timestamp_test"
            },
            "timestamp": "2025-09-27T00:00:00Z"
        }
        
        import datetime
        
        before_request = datetime.datetime.utcnow()
        response = client.post("/api/v1/webhooks/payment", json=webhook_data)
        after_request = datetime.datetime.utcnow()
        
        # Should return 200 OK
        assert response.status_code == 200
        
        data = response.json()
        
        # Validate processed_at timestamp
        processed_at = datetime.datetime.fromisoformat(
            data["processed_at"].replace('Z', '+00:00')
        ).replace(tzinfo=None)
        
        # Should be between request start and end
        assert before_request <= processed_at <= after_request
