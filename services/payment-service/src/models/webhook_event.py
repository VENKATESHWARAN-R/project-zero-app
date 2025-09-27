"""
Webhook Event model for the Payment Processing Service.

This module defines the Webhook Event entity for tracking simulated
webhook notifications for payment status updates.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional
from uuid import uuid4

from sqlalchemy import (
    Column, String, Integer, DateTime, Text, ForeignKey,
    Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class WebhookEventType(str, Enum):
    """Webhook event type enumeration."""
    PAYMENT_INITIATED = "PAYMENT_INITIATED"
    PAYMENT_COMPLETED = "PAYMENT_COMPLETED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_CANCELLED = "PAYMENT_CANCELLED"


class WebhookDeliveryStatus(str, Enum):
    """Webhook delivery status enumeration."""
    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class WebhookEvent(Base):
    """
    Webhook Event model for tracking simulated webhook notifications.
    
    Tracks webhook events for payment status updates with delivery status,
    retry logic, and comprehensive logging for debugging and monitoring.
    
    Attributes:
        id: Unique webhook event identifier (UUID)
        payment_id: Reference to related payment (UUID)
        event_type: Type of webhook event (enum)
        payload: Webhook payload data (JSON)
        endpoint_url: Target webhook URL
        status: Delivery status (enum)
        attempts: Number of delivery attempts
        last_attempt_at: Last delivery attempt timestamp (optional)
        next_retry_at: Next retry attempt timestamp (optional)
        created_at: Event creation timestamp
        delivered_at: Successful delivery timestamp (optional)
        error_message: Last delivery error message (optional)
    """
    
    __tablename__ = "webhook_events"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # Foreign key
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payment_transactions.id"), nullable=False, index=True)
    
    # Event details
    event_type = Column(SQLEnum(WebhookEventType), nullable=False)
    payload = Column(JSON, nullable=False)
    endpoint_url = Column(Text, nullable=False)
    
    # Delivery tracking
    status = Column(SQLEnum(WebhookDeliveryStatus), nullable=False, default=WebhookDeliveryStatus.PENDING, index=True)
    attempts = Column(Integer, nullable=False, default=0)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    next_retry_at = Column(DateTime(timezone=True), nullable=True, index=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    
    # Relationships
    payment = relationship("PaymentTransaction", back_populates="webhook_events")
    
    # Indexes for performance optimization
    __table_args__ = (
        Index('idx_webhook_payment_type', 'payment_id', 'event_type'),
        Index('idx_webhook_status_retry', 'status', 'next_retry_at'),
        Index('idx_webhook_created_status', 'created_at', 'status'),
    )
    
    # Retry configuration
    MAX_RETRY_ATTEMPTS = 5
    RETRY_DELAYS = [60, 300, 900, 3600, 7200]  # 1min, 5min, 15min, 1hr, 2hr
    
    def __init__(self, **kwargs):
        """Initialize webhook event with validation."""
        super().__init__(**kwargs)
        self._validate_payload()
        self._validate_endpoint_url()
    
    def _validate_payload(self):
        """Validate webhook payload is valid JSON."""
        if not self.payload or not isinstance(self.payload, dict):
            raise ValueError("Webhook payload must be a valid dictionary")
        
        # Ensure required fields are present
        required_fields = ["event_type", "payment_id", "timestamp"]
        for field in required_fields:
            if field not in self.payload:
                raise ValueError(f"Webhook payload must include {field}")
    
    def _validate_endpoint_url(self):
        """Validate endpoint URL format."""
        if not self.endpoint_url or not self.endpoint_url.startswith(("http://", "https://")):
            raise ValueError("Endpoint URL must be a valid HTTP/HTTPS URL")
    
    @classmethod
    def create_payment_initiated_event(
        cls,
        payment_id: str,
        endpoint_url: str,
        payment_data: Dict[str, Any]
    ) -> "WebhookEvent":
        """
        Create webhook event for payment initiation.
        
        Args:
            payment_id: Payment transaction ID
            endpoint_url: Target webhook URL
            payment_data: Payment information for payload
            
        Returns:
            WebhookEvent: New webhook event
        """
        payload = {
            "event_type": WebhookEventType.PAYMENT_INITIATED.value,
            "payment_id": payment_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "order_id": payment_data.get("order_id"),
                "amount": payment_data.get("amount"),
                "currency": payment_data.get("currency", "USD"),
                "status": "PENDING"
            }
        }
        
        return cls(
            payment_id=payment_id,
            event_type=WebhookEventType.PAYMENT_INITIATED,
            payload=payload,
            endpoint_url=endpoint_url
        )
    
    @classmethod
    def create_payment_completed_event(
        cls,
        payment_id: str,
        endpoint_url: str,
        payment_data: Dict[str, Any],
        gateway_transaction_id: Optional[str] = None
    ) -> "WebhookEvent":
        """
        Create webhook event for successful payment completion.
        
        Args:
            payment_id: Payment transaction ID
            endpoint_url: Target webhook URL
            payment_data: Payment information for payload
            gateway_transaction_id: Gateway transaction reference
            
        Returns:
            WebhookEvent: New webhook event
        """
        payload = {
            "event_type": WebhookEventType.PAYMENT_COMPLETED.value,
            "payment_id": payment_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "order_id": payment_data.get("order_id"),
                "amount": payment_data.get("amount"),
                "currency": payment_data.get("currency", "USD"),
                "status": "COMPLETED",
                "gateway_transaction_id": gateway_transaction_id,
                "processed_at": datetime.utcnow().isoformat()
            }
        }
        
        return cls(
            payment_id=payment_id,
            event_type=WebhookEventType.PAYMENT_COMPLETED,
            payload=payload,
            endpoint_url=endpoint_url
        )
    
    @classmethod
    def create_payment_failed_event(
        cls,
        payment_id: str,
        endpoint_url: str,
        payment_data: Dict[str, Any],
        failure_reason: str,
        error_code: Optional[str] = None
    ) -> "WebhookEvent":
        """
        Create webhook event for payment failure.
        
        Args:
            payment_id: Payment transaction ID
            endpoint_url: Target webhook URL
            payment_data: Payment information for payload
            failure_reason: Human-readable failure reason
            error_code: Machine-readable error code
            
        Returns:
            WebhookEvent: New webhook event
        """
        payload = {
            "event_type": WebhookEventType.PAYMENT_FAILED.value,
            "payment_id": payment_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "order_id": payment_data.get("order_id"),
                "amount": payment_data.get("amount"),
                "currency": payment_data.get("currency", "USD"),
                "status": "FAILED",
                "failure_reason": failure_reason,
                "error_code": error_code,
                "failed_at": datetime.utcnow().isoformat()
            }
        }
        
        return cls(
            payment_id=payment_id,
            event_type=WebhookEventType.PAYMENT_FAILED,
            payload=payload,
            endpoint_url=endpoint_url
        )
    
    @classmethod
    def create_payment_cancelled_event(
        cls,
        payment_id: str,
        endpoint_url: str,
        payment_data: Dict[str, Any],
        cancellation_reason: str = "Payment cancelled by user"
    ) -> "WebhookEvent":
        """
        Create webhook event for payment cancellation.
        
        Args:
            payment_id: Payment transaction ID
            endpoint_url: Target webhook URL
            payment_data: Payment information for payload
            cancellation_reason: Reason for cancellation
            
        Returns:
            WebhookEvent: New webhook event
        """
        payload = {
            "event_type": WebhookEventType.PAYMENT_CANCELLED.value,
            "payment_id": payment_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "order_id": payment_data.get("order_id"),
                "amount": payment_data.get("amount"),
                "currency": payment_data.get("currency", "USD"),
                "status": "CANCELLED",
                "cancellation_reason": cancellation_reason,
                "cancelled_at": datetime.utcnow().isoformat()
            }
        }
        
        return cls(
            payment_id=payment_id,
            event_type=WebhookEventType.PAYMENT_CANCELLED,
            payload=payload,
            endpoint_url=endpoint_url
        )
    
    def can_retry(self) -> bool:
        """Check if webhook can be retried."""
        return (
            self.status in [WebhookDeliveryStatus.PENDING, WebhookDeliveryStatus.FAILED] and
            self.attempts < self.MAX_RETRY_ATTEMPTS
        )
    
    def should_retry_now(self) -> bool:
        """Check if webhook should be retried now."""
        if not self.can_retry():
            return False
        
        if not self.next_retry_at:
            return True  # First attempt
        
        return datetime.utcnow() >= self.next_retry_at
    
    def schedule_retry(self):
        """Schedule next retry attempt with exponential backoff."""
        if not self.can_retry():
            return
        
        if self.attempts < len(self.RETRY_DELAYS):
            delay_seconds = self.RETRY_DELAYS[self.attempts]
        else:
            delay_seconds = self.RETRY_DELAYS[-1]  # Use last delay for remaining attempts
        
        self.next_retry_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
        self.status = WebhookDeliveryStatus.PENDING
    
    def mark_delivery_attempt(self, success: bool, error_message: Optional[str] = None):
        """
        Mark a delivery attempt and update status.
        
        Args:
            success: Whether delivery was successful
            error_message: Error message if delivery failed
        """
        self.attempts += 1
        self.last_attempt_at = datetime.utcnow()
        
        if success:
            self.status = WebhookDeliveryStatus.DELIVERED
            self.delivered_at = datetime.utcnow()
            self.next_retry_at = None
            self.error_message = None
        else:
            self.error_message = error_message
            
            if self.can_retry():
                self.schedule_retry()
            else:
                self.status = WebhookDeliveryStatus.FAILED
                self.next_retry_at = None
    
    def cancel_delivery(self, reason: str = "Delivery cancelled"):
        """
        Cancel webhook delivery.
        
        Args:
            reason: Reason for cancellation
        """
        self.status = WebhookDeliveryStatus.CANCELLED
        self.next_retry_at = None
        self.error_message = reason
    
    def is_delivered(self) -> bool:
        """Check if webhook was successfully delivered."""
        return self.status == WebhookDeliveryStatus.DELIVERED
    
    def is_failed(self) -> bool:
        """Check if webhook delivery failed permanently."""
        return self.status == WebhookDeliveryStatus.FAILED
    
    def is_pending(self) -> bool:
        """Check if webhook delivery is pending."""
        return self.status == WebhookDeliveryStatus.PENDING
    
    def get_retry_count_remaining(self) -> int:
        """Get number of retry attempts remaining."""
        return max(0, self.MAX_RETRY_ATTEMPTS - self.attempts)
    
    def get_next_retry_delay(self) -> Optional[int]:
        """Get delay in seconds until next retry attempt."""
        if not self.next_retry_at:
            return None
        
        delay = (self.next_retry_at - datetime.utcnow()).total_seconds()
        return max(0, int(delay))
    
    def to_dict(self) -> dict:
        """Convert webhook event to dictionary for API responses."""
        return {
            "id": str(self.id),
            "payment_id": str(self.payment_id),
            "event_type": self.event_type.value,
            "payload": self.payload,
            "endpoint_url": self.endpoint_url,
            "status": self.status.value,
            "attempts": self.attempts,
            "last_attempt_at": self.last_attempt_at.isoformat() if self.last_attempt_at else None,
            "next_retry_at": self.next_retry_at.isoformat() if self.next_retry_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def to_delivery_dict(self) -> dict:
        """Convert webhook event to dictionary for delivery monitoring."""
        return {
            "id": str(self.id),
            "event_type": self.event_type.value,
            "status": self.status.value,
            "attempts": self.attempts,
            "retry_count_remaining": self.get_retry_count_remaining(),
            "next_retry_delay_seconds": self.get_next_retry_delay(),
            "error_message": self.error_message,
        }
    
    def __repr__(self):
        return f"<WebhookEvent(id={self.id}, payment_id={self.payment_id}, type={self.event_type}, status={self.status})>"
