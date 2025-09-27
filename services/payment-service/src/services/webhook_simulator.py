"""
Webhook Simulator for the Payment Processing Service.

This module provides realistic webhook delivery simulation with async processing,
retry logic, and comprehensive delivery tracking.
"""

import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

import httpx
from sqlalchemy.orm import Session

from ..models.webhook_event import WebhookEvent, WebhookEventType, WebhookDeliveryStatus
from ..models.payment import PaymentTransaction


class WebhookConfig:
    """Configuration for webhook simulator."""
    
    def __init__(self):
        # Webhook simulation settings
        self.simulation_enabled = os.getenv("WEBHOOK_SIMULATION_ENABLED", "true").lower() == "true"
        self.delivery_delay_min = int(os.getenv("WEBHOOK_DELAY_MIN", "500"))  # ms
        self.delivery_delay_max = int(os.getenv("WEBHOOK_DELAY_MAX", "2000"))  # ms
        
        # Retry settings
        self.max_retry_attempts = int(os.getenv("WEBHOOK_MAX_RETRIES", "5"))
        self.retry_delays = [60, 300, 900, 3600, 7200]  # seconds: 1min, 5min, 15min, 1hr, 2hr
        
        # Delivery simulation settings
        self.success_rate = float(os.getenv("WEBHOOK_SUCCESS_RATE", "0.95"))
        self.timeout_seconds = int(os.getenv("WEBHOOK_TIMEOUT", "30"))
        
        # Default webhook endpoints for testing
        self.default_endpoints = {
            "order_service": os.getenv("ORDER_SERVICE_WEBHOOK_URL", "http://localhost:8008/webhooks/payment"),
            "notification_service": os.getenv("NOTIFICATION_SERVICE_WEBHOOK_URL", "http://localhost:8010/webhooks/payment"),
        }


class WebhookDeliveryResult:
    """Result of webhook delivery attempt."""
    
    def __init__(
        self,
        success: bool,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        error_message: Optional[str] = None,
        delivery_time_ms: Optional[int] = None
    ):
        self.success = success
        self.status_code = status_code
        self.response_body = response_body
        self.error_message = error_message
        self.delivery_time_ms = delivery_time_ms
        self.attempted_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "status_code": self.status_code,
            "response_body": self.response_body,
            "error_message": self.error_message,
            "delivery_time_ms": self.delivery_time_ms,
            "attempted_at": self.attempted_at.isoformat(),
        }


class WebhookSimulator:
    """
    Webhook simulator with realistic delivery behavior.
    
    Provides async webhook delivery with configurable delays, retry logic,
    and comprehensive tracking for payment status updates.
    """
    
    def __init__(self, config: Optional[WebhookConfig] = None):
        self.config = config or WebhookConfig()
        self._delivery_queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start the webhook delivery worker."""
        if self._running:
            return
        
        self._running = True
        self._worker_task = asyncio.create_task(self._delivery_worker())
    
    async def stop(self):
        """Stop the webhook delivery worker."""
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
    
    async def create_payment_webhook(
        self,
        payment: PaymentTransaction,
        event_type: WebhookEventType,
        endpoints: Optional[List[str]] = None,
        session: Optional[Session] = None
    ) -> List[WebhookEvent]:
        """
        Create webhook events for payment status change.
        
        Args:
            payment: Payment transaction
            event_type: Type of webhook event
            endpoints: List of webhook endpoints (uses defaults if None)
            session: Database session
            
        Returns:
            List[WebhookEvent]: Created webhook events
        """
        if not self.config.simulation_enabled:
            return []
        
        if endpoints is None:
            endpoints = list(self.config.default_endpoints.values())
        
        webhook_events = []
        
        for endpoint_url in endpoints:
            # Create webhook event based on type
            if event_type == WebhookEventType.PAYMENT_INITIATED:
                webhook_event = WebhookEvent.create_payment_initiated_event(
                    payment_id=str(payment.id),
                    endpoint_url=endpoint_url,
                    payment_data={
                        "order_id": str(payment.order_id),
                        "amount": payment.amount,
                        "currency": payment.currency,
                    }
                )
            elif event_type == WebhookEventType.PAYMENT_COMPLETED:
                webhook_event = WebhookEvent.create_payment_completed_event(
                    payment_id=str(payment.id),
                    endpoint_url=endpoint_url,
                    payment_data={
                        "order_id": str(payment.order_id),
                        "amount": payment.amount,
                        "currency": payment.currency,
                    },
                    gateway_transaction_id=payment.gateway_transaction_id
                )
            elif event_type == WebhookEventType.PAYMENT_FAILED:
                webhook_event = WebhookEvent.create_payment_failed_event(
                    payment_id=str(payment.id),
                    endpoint_url=endpoint_url,
                    payment_data={
                        "order_id": str(payment.order_id),
                        "amount": payment.amount,
                        "currency": payment.currency,
                    },
                    failure_reason=payment.failure_reason or "Payment processing failed"
                )
            elif event_type == WebhookEventType.PAYMENT_CANCELLED:
                webhook_event = WebhookEvent.create_payment_cancelled_event(
                    payment_id=str(payment.id),
                    endpoint_url=endpoint_url,
                    payment_data={
                        "order_id": str(payment.order_id),
                        "amount": payment.amount,
                        "currency": payment.currency,
                    }
                )
            else:
                continue
            
            webhook_events.append(webhook_event)
            
            # Save to database if session provided
            if session:
                session.add(webhook_event)
            
            # Queue for delivery
            await self._delivery_queue.put(webhook_event)
        
        return webhook_events
    
    async def deliver_webhook(self, webhook_event: WebhookEvent) -> WebhookDeliveryResult:
        """
        Deliver a single webhook event.
        
        Args:
            webhook_event: Webhook event to deliver
            
        Returns:
            WebhookDeliveryResult: Delivery result
        """
        start_time = datetime.utcnow()
        
        # Simulate delivery delay
        await self._simulate_delivery_delay()
        
        # Check if delivery should succeed (for simulation)
        should_succeed = random.random() < self.config.success_rate
        
        if not should_succeed:
            # Simulate delivery failure
            error_messages = [
                "Connection timeout",
                "Service unavailable",
                "Invalid endpoint",
                "Authentication failed",
                "Rate limit exceeded"
            ]
            error_message = random.choice(error_messages)
            
            return WebhookDeliveryResult(
                success=False,
                status_code=random.choice([408, 503, 404, 401, 429]),
                error_message=error_message,
                delivery_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000)
            )
        
        # Attempt actual delivery
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "PaymentService-Webhook/1.0",
                    "X-Webhook-Event": webhook_event.event_type.value,
                    "X-Webhook-ID": str(webhook_event.id),
                    "X-Webhook-Timestamp": webhook_event.created_at.isoformat(),
                }
                
                response = await client.post(
                    webhook_event.endpoint_url,
                    json=webhook_event.payload,
                    headers=headers
                )
                
                delivery_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                # Consider 2xx status codes as successful
                success = 200 <= response.status_code < 300
                
                return WebhookDeliveryResult(
                    success=success,
                    status_code=response.status_code,
                    response_body=response.text[:1000],  # Limit response body size
                    delivery_time_ms=delivery_time
                )
        
        except httpx.TimeoutException:
            return WebhookDeliveryResult(
                success=False,
                error_message="Request timeout",
                delivery_time_ms=self.config.timeout_seconds * 1000
            )
        except httpx.ConnectError:
            return WebhookDeliveryResult(
                success=False,
                error_message="Connection failed",
                delivery_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000)
            )
        except Exception as e:
            return WebhookDeliveryResult(
                success=False,
                error_message=f"Delivery error: {str(e)}",
                delivery_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000)
            )
    
    async def process_webhook_delivery(
        self,
        webhook_event: WebhookEvent,
        session: Session
    ) -> WebhookDeliveryResult:
        """
        Process webhook delivery with retry logic.
        
        Args:
            webhook_event: Webhook event to deliver
            session: Database session for updates
            
        Returns:
            WebhookDeliveryResult: Final delivery result
        """
        result = await self.deliver_webhook(webhook_event)
        
        # Update webhook event with delivery result
        webhook_event.mark_delivery_attempt(
            success=result.success,
            error_message=result.error_message
        )
        
        # Commit the update
        session.commit()
        
        return result
    
    async def retry_failed_webhooks(self, session: Session) -> Dict[str, Any]:
        """
        Retry failed webhook deliveries that are due for retry.
        
        Args:
            session: Database session
            
        Returns:
            Dict[str, Any]: Retry statistics
        """
        # Query webhooks that need retry
        now = datetime.utcnow()
        failed_webhooks = session.query(WebhookEvent).filter(
            WebhookEvent.status == WebhookDeliveryStatus.PENDING,
            WebhookEvent.next_retry_at <= now,
            WebhookEvent.attempts < self.config.max_retry_attempts
        ).all()
        
        retry_stats = {
            "total_retries": len(failed_webhooks),
            "successful_retries": 0,
            "failed_retries": 0,
            "permanent_failures": 0
        }
        
        for webhook_event in failed_webhooks:
            result = await self.process_webhook_delivery(webhook_event, session)
            
            if result.success:
                retry_stats["successful_retries"] += 1
            else:
                if webhook_event.status == WebhookDeliveryStatus.FAILED:
                    retry_stats["permanent_failures"] += 1
                else:
                    retry_stats["failed_retries"] += 1
        
        return retry_stats
    
    async def _delivery_worker(self):
        """Background worker for processing webhook deliveries."""
        while self._running:
            try:
                # Wait for webhook event with timeout
                webhook_event = await asyncio.wait_for(
                    self._delivery_queue.get(),
                    timeout=1.0
                )
                
                # Process delivery (this would need a session in real implementation)
                # For now, just simulate the delivery
                await self.deliver_webhook(webhook_event)
                
            except asyncio.TimeoutError:
                # No webhooks to process, continue
                continue
            except asyncio.CancelledError:
                # Worker is being stopped
                break
            except Exception as e:
                # Log error and continue
                print(f"Webhook delivery worker error: {e}")
                continue
    
    async def _simulate_delivery_delay(self):
        """Simulate realistic delivery delay."""
        delay_ms = random.randint(
            self.config.delivery_delay_min,
            self.config.delivery_delay_max
        )
        await asyncio.sleep(delay_ms / 1000.0)
    
    def get_webhook_stats(self, session: Session) -> Dict[str, Any]:
        """
        Get webhook delivery statistics.
        
        Args:
            session: Database session
            
        Returns:
            Dict[str, Any]: Webhook statistics
        """
        # Query webhook statistics
        total_webhooks = session.query(WebhookEvent).count()
        delivered_webhooks = session.query(WebhookEvent).filter(
            WebhookEvent.status == WebhookDeliveryStatus.DELIVERED
        ).count()
        failed_webhooks = session.query(WebhookEvent).filter(
            WebhookEvent.status == WebhookDeliveryStatus.FAILED
        ).count()
        pending_webhooks = session.query(WebhookEvent).filter(
            WebhookEvent.status == WebhookDeliveryStatus.PENDING
        ).count()
        
        # Calculate success rate
        success_rate = (delivered_webhooks / total_webhooks) if total_webhooks > 0 else 0
        
        return {
            "total_webhooks": total_webhooks,
            "delivered_webhooks": delivered_webhooks,
            "failed_webhooks": failed_webhooks,
            "pending_webhooks": pending_webhooks,
            "success_rate": success_rate,
            "simulation_enabled": self.config.simulation_enabled,
            "default_endpoints": self.config.default_endpoints,
        }
    
    def validate_webhook_endpoint(self, endpoint_url: str) -> bool:
        """
        Validate webhook endpoint URL.
        
        Args:
            endpoint_url: Webhook endpoint URL
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            parsed = urlparse(endpoint_url)
            return (
                parsed.scheme in ("http", "https") and
                parsed.netloc and
                len(endpoint_url) <= 2048
            )
        except Exception:
            return False
    
    async def test_webhook_endpoint(self, endpoint_url: str) -> WebhookDeliveryResult:
        """
        Test webhook endpoint with a ping message.
        
        Args:
            endpoint_url: Webhook endpoint URL to test
            
        Returns:
            WebhookDeliveryResult: Test result
        """
        test_payload = {
            "event_type": "WEBHOOK_TEST",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "message": "Webhook endpoint test",
                "service": "payment-service"
            }
        }
        
        start_time = datetime.utcnow()
        
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "PaymentService-Webhook/1.0",
                    "X-Webhook-Event": "WEBHOOK_TEST",
                }
                
                response = await client.post(
                    endpoint_url,
                    json=test_payload,
                    headers=headers
                )
                
                delivery_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                success = 200 <= response.status_code < 300
                
                return WebhookDeliveryResult(
                    success=success,
                    status_code=response.status_code,
                    response_body=response.text[:500],
                    delivery_time_ms=delivery_time
                )
        
        except Exception as e:
            return WebhookDeliveryResult(
                success=False,
                error_message=str(e),
                delivery_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000)
            )


# Global webhook simulator instance
_webhook_simulator_instance: Optional[WebhookSimulator] = None


def get_webhook_simulator() -> WebhookSimulator:
    """Get singleton webhook simulator instance."""
    global _webhook_simulator_instance
    if _webhook_simulator_instance is None:
        _webhook_simulator_instance = WebhookSimulator()
    return _webhook_simulator_instance


async def start_webhook_simulator():
    """Start the global webhook simulator."""
    simulator = get_webhook_simulator()
    await simulator.start()


async def stop_webhook_simulator():
    """Stop the global webhook simulator."""
    simulator = get_webhook_simulator()
    await simulator.stop()
