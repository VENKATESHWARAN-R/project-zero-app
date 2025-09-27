"""
Unit tests for the Webhook Simulator service.

Tests webhook delivery simulation, retry logic, and comprehensive
webhook event handling for payment status updates.
"""

import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

import httpx

from src.services.webhook_simulator import (
    WebhookSimulator,
    WebhookConfig,
    WebhookDeliveryResult,
    get_webhook_simulator,
    start_webhook_simulator,
    stop_webhook_simulator
)
from src.models.webhook_event import WebhookEvent, WebhookEventType, WebhookDeliveryStatus
from src.models.payment import PaymentTransaction, PaymentStatus


class TestWebhookConfig:
    """Test webhook configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = WebhookConfig()
        
        assert config.simulation_enabled is True
        assert config.delivery_delay_min == 500
        assert config.delivery_delay_max == 2000
        assert config.max_retry_attempts == 5
        assert len(config.retry_delays) == 5
        assert config.success_rate == 0.95
        assert config.timeout_seconds == 30
        assert len(config.default_endpoints) == 2
    
    @patch.dict('os.environ', {
        'WEBHOOK_SIMULATION_ENABLED': 'false',
        'WEBHOOK_DELAY_MIN': '100',
        'WEBHOOK_DELAY_MAX': '1000',
        'WEBHOOK_SUCCESS_RATE': '0.8',
        'WEBHOOK_TIMEOUT': '15'
    })
    def test_config_from_environment(self):
        """Test configuration loading from environment variables."""
        config = WebhookConfig()
        
        assert config.simulation_enabled is False
        assert config.delivery_delay_min == 100
        assert config.delivery_delay_max == 1000
        assert config.success_rate == 0.8
        assert config.timeout_seconds == 15
    
    def test_retry_delays_configuration(self):
        """Test retry delays configuration."""
        config = WebhookConfig()
        
        # Should have exponential backoff pattern
        assert config.retry_delays[0] < config.retry_delays[1]
        assert config.retry_delays[1] < config.retry_delays[2]
        assert len(config.retry_delays) == config.max_retry_attempts


class TestWebhookDeliveryResult:
    """Test webhook delivery result."""
    
    def test_successful_delivery_result(self):
        """Test successful delivery result creation."""
        result = WebhookDeliveryResult(
            success=True,
            status_code=200,
            response_body="OK",
            delivery_time_ms=150
        )
        
        assert result.success is True
        assert result.status_code == 200
        assert result.response_body == "OK"
        assert result.delivery_time_ms == 150
        assert result.error_message is None
        assert isinstance(result.attempted_at, datetime)
    
    def test_failed_delivery_result(self):
        """Test failed delivery result creation."""
        result = WebhookDeliveryResult(
            success=False,
            error_message="Connection timeout",
            delivery_time_ms=30000
        )
        
        assert result.success is False
        assert result.error_message == "Connection timeout"
        assert result.delivery_time_ms == 30000
        assert result.status_code is None
        assert result.response_body is None
    
    def test_result_to_dict(self):
        """Test delivery result serialization."""
        result = WebhookDeliveryResult(
            success=True,
            status_code=200,
            response_body="OK",
            delivery_time_ms=150
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["success"] is True
        assert result_dict["status_code"] == 200
        assert result_dict["response_body"] == "OK"
        assert result_dict["delivery_time_ms"] == 150
        assert "attempted_at" in result_dict


class TestWebhookSimulator:
    """Test webhook simulator functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = WebhookConfig()
        self.config.delivery_delay_min = 1  # Reduce delays for testing
        self.config.delivery_delay_max = 5
        self.config.timeout_seconds = 1
        self.simulator = WebhookSimulator(self.config)
    
    def teardown_method(self):
        """Clean up after tests."""
        asyncio.create_task(self.simulator.stop())
    
    @pytest.mark.asyncio
    async def test_simulator_start_stop(self):
        """Test simulator start and stop functionality."""
        assert self.simulator._running is False
        
        await self.simulator.start()
        assert self.simulator._running is True
        assert self.simulator._worker_task is not None
        
        await self.simulator.stop()
        assert self.simulator._running is False
    
    def test_webhook_endpoint_validation(self):
        """Test webhook endpoint URL validation."""
        # Valid URLs
        assert self.simulator.validate_webhook_endpoint("http://localhost:8080/webhook") is True
        assert self.simulator.validate_webhook_endpoint("https://api.example.com/webhooks") is True
        
        # Invalid URLs
        assert self.simulator.validate_webhook_endpoint("invalid-url") is False
        assert self.simulator.validate_webhook_endpoint("ftp://example.com") is False
        assert self.simulator.validate_webhook_endpoint("") is False
        assert self.simulator.validate_webhook_endpoint("x" * 3000) is False  # Too long
    
    @pytest.mark.asyncio
    async def test_webhook_endpoint_test(self):
        """Test webhook endpoint testing functionality."""
        test_url = "http://httpbin.org/post"
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "OK"
            mock_post.return_value = mock_response
            
            result = await self.simulator.test_webhook_endpoint(test_url)
            
            assert result.success is True
            assert result.status_code == 200
            assert result.response_body == "OK"
            assert result.delivery_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_webhook_endpoint_test_failure(self):
        """Test webhook endpoint test with failure."""
        test_url = "http://invalid-endpoint.example.com"
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = httpx.ConnectError("Connection failed")
            
            result = await self.simulator.test_webhook_endpoint(test_url)
            
            assert result.success is False
            assert "Connection failed" in result.error_message
            assert result.delivery_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_successful_webhook_delivery(self):
        """Test successful webhook delivery."""
        # Force success
        self.config.success_rate = 1.0
        
        webhook_event = MagicMock()
        webhook_event.id = "webhook-123"
        webhook_event.event_type = WebhookEventType.PAYMENT_COMPLETED
        webhook_event.endpoint_url = "http://localhost:8080/webhook"
        webhook_event.payload = {"test": "data"}
        webhook_event.created_at = datetime.utcnow()
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "OK"
            mock_post.return_value = mock_response
            
            result = await self.simulator.deliver_webhook(webhook_event)
            
            assert result.success is True
            assert result.status_code == 200
            assert result.response_body == "OK"
            assert result.delivery_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_failed_webhook_delivery_simulation(self):
        """Test simulated webhook delivery failure."""
        # Force failure
        self.config.success_rate = 0.0
        
        webhook_event = MagicMock()
        webhook_event.id = "webhook-123"
        webhook_event.event_type = WebhookEventType.PAYMENT_FAILED
        webhook_event.endpoint_url = "http://localhost:8080/webhook"
        webhook_event.payload = {"test": "data"}
        webhook_event.created_at = datetime.utcnow()
        
        result = await self.simulator.deliver_webhook(webhook_event)
        
        assert result.success is False
        assert result.status_code in [408, 503, 404, 401, 429]
        assert result.error_message is not None
        assert result.delivery_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_webhook_delivery_timeout(self):
        """Test webhook delivery timeout handling."""
        webhook_event = MagicMock()
        webhook_event.id = "webhook-123"
        webhook_event.event_type = WebhookEventType.PAYMENT_COMPLETED
        webhook_event.endpoint_url = "http://localhost:8080/webhook"
        webhook_event.payload = {"test": "data"}
        webhook_event.created_at = datetime.utcnow()
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Request timeout")
            
            result = await self.simulator.deliver_webhook(webhook_event)
            
            assert result.success is False
            assert "timeout" in result.error_message.lower()
            assert result.delivery_time_ms == self.config.timeout_seconds * 1000
    
    @pytest.mark.asyncio
    async def test_webhook_delivery_connection_error(self):
        """Test webhook delivery connection error handling."""
        webhook_event = MagicMock()
        webhook_event.id = "webhook-123"
        webhook_event.event_type = WebhookEventType.PAYMENT_COMPLETED
        webhook_event.endpoint_url = "http://localhost:8080/webhook"
        webhook_event.payload = {"test": "data"}
        webhook_event.created_at = datetime.utcnow()
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = httpx.ConnectError("Connection failed")
            
            result = await self.simulator.deliver_webhook(webhook_event)
            
            assert result.success is False
            assert "Connection failed" in result.error_message
            assert result.delivery_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_create_payment_webhook_events(self):
        """Test creation of payment webhook events."""
        # Mock payment transaction
        payment = MagicMock()
        payment.id = "payment-123"
        payment.order_id = "order-456"
        payment.amount = 5000
        payment.currency = "USD"
        payment.gateway_transaction_id = "txn-789"
        payment.failure_reason = None
        
        # Mock session
        session = MagicMock()
        
        # Test payment completed event
        webhook_events = await self.simulator.create_payment_webhook(
            payment=payment,
            event_type=WebhookEventType.PAYMENT_COMPLETED,
            endpoints=["http://localhost:8080/webhook"],
            session=session
        )
        
        assert len(webhook_events) == 1
        webhook_event = webhook_events[0]
        
        assert webhook_event.payment_id == "payment-123"
        assert webhook_event.event_type == WebhookEventType.PAYMENT_COMPLETED
        assert webhook_event.endpoint_url == "http://localhost:8080/webhook"
        assert "order_id" in webhook_event.payload["data"]
        assert webhook_event.payload["data"]["amount"] == 5000
    
    @pytest.mark.asyncio
    async def test_create_payment_failed_webhook(self):
        """Test creation of payment failed webhook event."""
        # Mock payment transaction
        payment = MagicMock()
        payment.id = "payment-123"
        payment.order_id = "order-456"
        payment.amount = 5000
        payment.currency = "USD"
        payment.failure_reason = "Card declined"
        
        webhook_events = await self.simulator.create_payment_webhook(
            payment=payment,
            event_type=WebhookEventType.PAYMENT_FAILED,
            endpoints=["http://localhost:8080/webhook"]
        )
        
        assert len(webhook_events) == 1
        webhook_event = webhook_events[0]
        
        assert webhook_event.event_type == WebhookEventType.PAYMENT_FAILED
        assert "failure_reason" in webhook_event.payload
        assert webhook_event.payload["failure_reason"] == "Card declined"
    
    @pytest.mark.asyncio
    async def test_disabled_webhook_simulation(self):
        """Test behavior when webhook simulation is disabled."""
        self.config.simulation_enabled = False
        
        payment = MagicMock()
        payment.id = "payment-123"
        
        webhook_events = await self.simulator.create_payment_webhook(
            payment=payment,
            event_type=WebhookEventType.PAYMENT_COMPLETED
        )
        
        assert len(webhook_events) == 0
    
    @pytest.mark.asyncio
    async def test_process_webhook_delivery_with_session(self):
        """Test webhook delivery processing with database session."""
        webhook_event = MagicMock()
        webhook_event.id = "webhook-123"
        webhook_event.event_type = WebhookEventType.PAYMENT_COMPLETED
        webhook_event.endpoint_url = "http://localhost:8080/webhook"
        webhook_event.payload = {"test": "data"}
        webhook_event.created_at = datetime.utcnow()
        webhook_event.mark_delivery_attempt = MagicMock()
        
        session = MagicMock()
        
        # Force success
        self.config.success_rate = 1.0
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "OK"
            mock_post.return_value = mock_response
            
            result = await self.simulator.process_webhook_delivery(webhook_event, session)
            
            assert result.success is True
            webhook_event.mark_delivery_attempt.assert_called_once_with(
                success=True,
                error_message=None
            )
            session.commit.assert_called_once()
    
    def test_get_webhook_stats(self):
        """Test webhook statistics retrieval."""
        # Mock session and query results
        session = MagicMock()
        
        # Mock query chain
        mock_query = MagicMock()
        session.query.return_value = mock_query
        mock_query.count.return_value = 100
        mock_query.filter.return_value = mock_query
        
        # Set up different counts for different statuses
        def count_side_effect():
            if hasattr(count_side_effect, 'call_count'):
                count_side_effect.call_count += 1
            else:
                count_side_effect.call_count = 1
            
            # Return different values for different calls
            if count_side_effect.call_count == 1:
                return 100  # total
            elif count_side_effect.call_count == 2:
                return 80   # delivered
            elif count_side_effect.call_count == 3:
                return 15   # failed
            else:
                return 5    # pending
        
        mock_query.count.side_effect = count_side_effect
        
        stats = self.simulator.get_webhook_stats(session)
        
        assert stats["total_webhooks"] == 100
        assert stats["delivered_webhooks"] == 80
        assert stats["failed_webhooks"] == 15
        assert stats["pending_webhooks"] == 5
        assert stats["success_rate"] == 0.8
        assert stats["simulation_enabled"] == self.config.simulation_enabled
        assert "default_endpoints" in stats


class TestWebhookSimulatorSingleton:
    """Test webhook simulator singleton functionality."""
    
    @pytest.mark.asyncio
    async def test_singleton_instance(self):
        """Test that get_webhook_simulator returns singleton instance."""
        simulator1 = get_webhook_simulator()
        simulator2 = get_webhook_simulator()
        
        assert simulator1 is simulator2
        assert isinstance(simulator1, WebhookSimulator)
    
    @pytest.mark.asyncio
    async def test_global_start_stop_functions(self):
        """Test global start and stop functions."""
        # Test start
        await start_webhook_simulator()
        simulator = get_webhook_simulator()
        assert simulator._running is True
        
        # Test stop
        await stop_webhook_simulator()
        assert simulator._running is False


class TestWebhookSimulatorIntegration:
    """Integration tests for webhook simulator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = WebhookConfig()
        self.config.delivery_delay_min = 1
        self.config.delivery_delay_max = 5
        self.simulator = WebhookSimulator(self.config)
    
    @pytest.mark.asyncio
    async def test_concurrent_webhook_deliveries(self):
        """Test concurrent webhook deliveries."""
        # Create multiple webhook events
        webhook_events = []
        for i in range(5):
            webhook_event = MagicMock()
            webhook_event.id = f"webhook-{i}"
            webhook_event.event_type = WebhookEventType.PAYMENT_COMPLETED
            webhook_event.endpoint_url = f"http://localhost:808{i}/webhook"
            webhook_event.payload = {"test": f"data-{i}"}
            webhook_event.created_at = datetime.utcnow()
            webhook_events.append(webhook_event)
        
        # Force success for all
        self.config.success_rate = 1.0
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "OK"
            mock_post.return_value = mock_response
            
            # Deliver all webhooks concurrently
            tasks = [
                self.simulator.deliver_webhook(webhook_event)
                for webhook_event in webhook_events
            ]
            results = await asyncio.gather(*tasks)
            
            # Verify all deliveries
            assert len(results) == 5
            for result in results:
                assert result.success is True
                assert result.status_code == 200
    
    @pytest.mark.asyncio
    async def test_webhook_delivery_with_retry_logic(self):
        """Test webhook delivery with retry logic simulation."""
        # Mock session for retry testing
        session = MagicMock()
        
        # Mock failed webhooks query
        failed_webhook = MagicMock()
        failed_webhook.id = "webhook-123"
        failed_webhook.status = WebhookDeliveryStatus.PENDING
        failed_webhook.next_retry_at = datetime.utcnow() - timedelta(minutes=1)
        failed_webhook.attempts = 2
        failed_webhook.event_type = WebhookEventType.PAYMENT_COMPLETED
        failed_webhook.endpoint_url = "http://localhost:8080/webhook"
        failed_webhook.payload = {"test": "data"}
        failed_webhook.created_at = datetime.utcnow()
        failed_webhook.mark_delivery_attempt = MagicMock()
        
        mock_query = MagicMock()
        session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [failed_webhook]
        
        # Force success for retry
        self.config.success_rate = 1.0
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "OK"
            mock_post.return_value = mock_response
            
            retry_stats = await self.simulator.retry_failed_webhooks(session)
            
            assert retry_stats["total_retries"] == 1
            assert retry_stats["successful_retries"] == 1
            assert retry_stats["failed_retries"] == 0
