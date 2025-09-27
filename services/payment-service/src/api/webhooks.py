"""
Webhook API endpoints.

This module implements webhook endpoints for receiving simulated
payment gateway notifications and processing webhook events.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..models.database import get_session
from ..models.payment import PaymentTransaction, PaymentStatus
from ..models.payment_status_history import PaymentStatusHistory
from ..models.webhook_event import WebhookEvent, WebhookEventType, WebhookDeliveryStatus
# from ..services.webhook_simulator import get_webhook_simulator  # Not used in this module


router = APIRouter()


# Pydantic models for request/response
class WebhookPayload(BaseModel):
    """Webhook payload model."""
    event_type: str = Field(..., description="Type of webhook event")
    payment_id: UUID = Field(..., description="Payment transaction ID")
    data: Dict[str, Any] = Field(..., description="Event-specific data")
    timestamp: Optional[str] = Field(None, description="Event timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "event_type": "PAYMENT_COMPLETED",
                "payment_id": "123e4567-e89b-12d3-a456-426614174000",
                "data": {
                    "gateway_transaction_id": "mock_txn_abc123",
                    "amount": 2999,
                    "currency": "USD",
                    "processing_time_ms": 1500
                },
                "timestamp": "2025-09-27T00:00:00Z"
            }
        }


class WebhookResponse(BaseModel):
    """Webhook response model."""
    received: bool = Field(..., description="Whether webhook was received successfully")
    processed_at: datetime = Field(..., description="Processing timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "received": True,
                "processed_at": "2025-09-27T00:00:00Z"
            }
        }


@router.post("/webhooks/payment", response_model=WebhookResponse)
async def receive_payment_webhook(
    webhook_payload: WebhookPayload,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Receive simulated payment gateway webhooks.
    
    This endpoint processes webhook notifications from the mock payment gateway,
    updating payment status and creating audit trail entries.
    
    Note: This endpoint does not require authentication as it simulates
    external gateway webhooks. In production, webhook signature validation
    would be implemented.
    """
    processed_at = datetime.utcnow()
    
    try:
        # Validate event type
        try:
            event_type = WebhookEventType(webhook_payload.event_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": f"Invalid event type: {webhook_payload.event_type}",
                    "code": "invalid_event_type",
                    "timestamp": processed_at.isoformat()
                }
            )
        
        # Find the payment transaction
        payment = session.query(PaymentTransaction).filter(
            PaymentTransaction.id == webhook_payload.payment_id
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Payment not found",
                    "code": "payment_not_found",
                    "timestamp": processed_at.isoformat()
                }
            )
        
        # Process webhook based on event type
        webhook_data = webhook_payload.data
        
        if event_type == WebhookEventType.PAYMENT_INITIATED:
            await _process_payment_initiated_webhook(payment, webhook_data, session)
            
        elif event_type == WebhookEventType.PAYMENT_COMPLETED:
            await _process_payment_completed_webhook(payment, webhook_data, session)
            
        elif event_type == WebhookEventType.PAYMENT_FAILED:
            await _process_payment_failed_webhook(payment, webhook_data, session)
            
        elif event_type == WebhookEventType.PAYMENT_CANCELLED:
            await _process_payment_cancelled_webhook(payment, webhook_data, session)
        
        # Create webhook event record for audit trail
        webhook_event = WebhookEvent(
            payment_id=webhook_payload.payment_id,
            event_type=event_type,
            payload=webhook_payload.dict(),
            endpoint_url=str(request.url),
            status=WebhookDeliveryStatus.DELIVERED,
            attempts=1,
            last_attempt_at=processed_at
        )
        
        session.add(webhook_event)
        session.commit()
        
        return WebhookResponse(
            received=True,
            processed_at=processed_at
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        # Handle unexpected errors
        session.rollback()
        
        # Create failed webhook event record
        try:
            webhook_event = WebhookEvent(
                payment_id=webhook_payload.payment_id,
                event_type=WebhookEventType(webhook_payload.event_type),
                payload=webhook_payload.dict(),
                endpoint_url=str(request.url),
                status=WebhookDeliveryStatus.FAILED,
                attempts=1,
                last_attempt_at=processed_at
            )
            session.add(webhook_event)
            session.commit()
        except Exception:
            pass  # Don't fail if we can't log the webhook failure
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Webhook processing failed: {str(e)}",
                "code": "webhook_processing_error",
                "timestamp": processed_at.isoformat()
            }
        )


async def _process_payment_initiated_webhook(
    payment: PaymentTransaction,
    webhook_data: Dict[str, Any],
    session: Session
):
    """Process payment initiated webhook."""
    # Update payment status if not already set
    if payment.status == PaymentStatus.PENDING:
        payment.status = PaymentStatus.PROCESSING
        payment.updated_at = datetime.utcnow()
        
        # Create status history entry
        history = PaymentStatusHistory.create_processing_entry(
            payment_id=str(payment.id),
            reason="Payment processing initiated via webhook"
        )
        session.add(history)


async def _process_payment_completed_webhook(
    payment: PaymentTransaction,
    webhook_data: Dict[str, Any],
    session: Session
):
    """Process payment completed webhook."""
    # Update payment status and details
    payment.status = PaymentStatus.COMPLETED
    payment.processed_at = datetime.utcnow()
    payment.updated_at = payment.processed_at
    
    # Update gateway transaction ID if provided
    if 'gateway_transaction_id' in webhook_data:
        payment.gateway_transaction_id = webhook_data['gateway_transaction_id']
    
    # Create status history entry
    processing_time_ms = webhook_data.get('processing_time_ms')
    gateway_transaction_id = webhook_data.get('gateway_transaction_id')
    
    history = PaymentStatusHistory.create_completion_entry(
        payment_id=str(payment.id),
        gateway_transaction_id=gateway_transaction_id,
        processing_time_ms=processing_time_ms,
        reason="Payment completed via webhook notification"
    )
    session.add(history)
    
    # Notify order service of successful payment (in background)
    try:
        await _notify_order_service_payment_completed(payment)
    except Exception as e:
        # Log error but don't fail webhook processing
        print(f"Failed to notify order service: {e}")


async def _process_payment_failed_webhook(
    payment: PaymentTransaction,
    webhook_data: Dict[str, Any],
    session: Session
):
    """Process payment failed webhook."""
    # Update payment status and failure details
    payment.status = PaymentStatus.FAILED
    payment.updated_at = datetime.utcnow()
    
    # Set failure reason from webhook data
    failure_reason = webhook_data.get('failure_reason', 'Payment failed')
    payment.failure_reason = failure_reason
    
    # Create status history entry
    error_code = webhook_data.get('error_code')
    gateway_response = webhook_data.get('gateway_response')
    
    history = PaymentStatusHistory.create_failure_entry(
        payment_id=str(payment.id),
        failure_reason=failure_reason,
        error_code=error_code,
        gateway_response=gateway_response,
        reason="Payment failed via webhook notification"
    )
    session.add(history)


async def _process_payment_cancelled_webhook(
    payment: PaymentTransaction,
    webhook_data: Dict[str, Any],
    session: Session
):
    """Process payment cancelled webhook."""
    # Update payment status
    payment.status = PaymentStatus.CANCELLED
    payment.updated_at = datetime.utcnow()
    
    # Set cancellation reason from webhook data
    cancellation_reason = webhook_data.get('cancellation_reason', 'Payment cancelled')
    
    # Create status history entry
    history = PaymentStatusHistory.create_cancellation_entry(
        payment_id=str(payment.id),
        reason=cancellation_reason
    )
    session.add(history)


async def _notify_order_service_payment_completed(payment: PaymentTransaction):
    """
    Notify order service of successful payment completion.
    
    This function would integrate with the order service to update
    order status after successful payment.
    """
    import httpx
    import os
    
    order_service_url = os.getenv("ORDER_SERVICE_URL", "http://localhost:8008")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{order_service_url}/api/v1/orders/{payment.order_id}/payment-completed",
                json={
                    "payment_id": str(payment.id),
                    "amount": payment.amount,
                    "currency": payment.currency,
                    "gateway_transaction_id": payment.gateway_transaction_id,
                    "processed_at": payment.processed_at.isoformat() if payment.processed_at else None
                },
                headers={
                    "Content-Type": "application/json",
                    "X-Service-Name": "payment-service"
                }
            )
            
            if response.status_code not in [200, 201, 204]:
                raise Exception(f"Order service returned status {response.status_code}: {response.text}")
                
    except Exception as e:
        # Log the error for monitoring
        print(f"Failed to notify order service for payment {payment.id}: {e}")
        raise


# Additional webhook endpoints for testing and monitoring

@router.get("/webhooks/events/{payment_id}")
async def get_webhook_events(
    payment_id: UUID,
    session: Session = Depends(get_session)
):
    """
    Get webhook events for a specific payment (for debugging/monitoring).
    
    This endpoint is useful for debugging webhook delivery issues
    and monitoring webhook event history.
    """
    # Find webhook events for the payment
    webhook_events = session.query(WebhookEvent).filter(
        WebhookEvent.payment_id == payment_id
    ).order_by(WebhookEvent.created_at.desc()).all()
    
    if not webhook_events:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "No webhook events found for payment",
                "code": "webhook_events_not_found",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Convert to response format
    events = []
    for event in webhook_events:
        events.append({
            "id": str(event.id),
            "payment_id": str(event.payment_id),
            "event_type": event.event_type.value,
            "status": event.status.value,
            "attempts": event.attempts,
            "created_at": event.created_at.isoformat(),
            "last_attempt_at": event.last_attempt_at.isoformat() if event.last_attempt_at else None,
            "next_retry_at": event.next_retry_at.isoformat() if event.next_retry_at else None,
            "payload": event.payload
        })
    
    return {
        "payment_id": str(payment_id),
        "webhook_events": events,
        "total_events": len(events)
    }


@router.post("/webhooks/test")
async def test_webhook_endpoint():
    """
    Test webhook endpoint for connectivity verification.
    
    This endpoint can be used to test webhook connectivity
    and verify that the webhook service is responding correctly.
    """
    return {
        "status": "ok",
        "message": "Webhook endpoint is working correctly",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "payment-service",
        "version": "1.0.0"
    }
