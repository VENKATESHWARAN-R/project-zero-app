"""
Payment processing API endpoints.

This module implements the payment processing endpoints including
payment creation, status checking, and payment history retrieval.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..models.database import get_session
from ..models.payment import PaymentTransaction, PaymentStatus
from ..models.payment_method import PaymentMethod
from ..models.payment_status_history import PaymentStatusHistory
from ..models.webhook_event import WebhookEventType
from ..services.payment_processor import get_payment_processor
from ..services.payment_validator import get_payment_validator
from ..services.webhook_simulator import get_webhook_simulator
from ..utils.security import get_current_user_id


router = APIRouter()


# Pydantic models for request/response
class PaymentRequest(BaseModel):
    """Payment request model."""
    order_id: UUID = Field(..., description="Order ID to process payment for")
    payment_method_id: UUID = Field(..., description="Payment method to use")
    amount: int = Field(..., gt=0, description="Payment amount in cents")
    currency: str = Field(default="USD", description="Payment currency code")
    description: Optional[str] = Field(None, max_length=255, description="Payment description")


class PaymentResponse(BaseModel):
    """Payment response model."""
    id: UUID
    order_id: UUID
    user_id: UUID
    payment_method_id: UUID
    amount: int
    currency: str
    status: str
    gateway_transaction_id: Optional[str]
    failure_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]


class PaymentStatusResponse(BaseModel):
    """Payment status response model."""
    payment_id: UUID
    status: str
    updated_at: datetime


class PaymentHistoryResponse(BaseModel):
    """Payment history response model."""
    payments: List[PaymentResponse]
    total: int
    limit: int
    offset: int




@router.post("/payments", response_model=PaymentResponse, status_code=201)
async def process_payment(
    payment_request: PaymentRequest,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Process a payment for an order.
    
    Creates a new payment transaction and processes it through the
    mock payment processor with realistic simulation.
    """
    # Get services
    validator = get_payment_validator()
    processor = get_payment_processor()
    webhook_simulator = get_webhook_simulator()
    
    # Validate payment request
    validation_result = validator.validate_payment_request(
        amount=payment_request.amount,
        currency=payment_request.currency,
        order_id=str(payment_request.order_id),
        payment_method_id=str(payment_request.payment_method_id),
        user_id=str(user_id),
        description=payment_request.description
    )
    
    if not validation_result.is_valid:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid payment request",
                "code": "validation_error",
                "details": validation_result.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Check if payment method exists and belongs to user
    payment_method = session.query(PaymentMethod).filter(
        PaymentMethod.id == payment_request.payment_method_id,
        PaymentMethod.user_id == user_id,
        PaymentMethod.is_active
    ).first()
    
    if not payment_method:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Payment method not found or not accessible",
                "code": "payment_method_not_found",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Check if payment method can be used
    if not payment_method.can_be_used():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Payment method cannot be used (expired or inactive)",
                "code": "payment_method_unusable",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Check for existing successful payment for this order
    existing_payment = session.query(PaymentTransaction).filter(
        PaymentTransaction.order_id == payment_request.order_id,
        PaymentTransaction.status == PaymentStatus.COMPLETED
    ).first()
    
    if existing_payment:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Payment already exists for this order",
                "code": "payment_already_exists",
                "details": {"existing_payment_id": str(existing_payment.id)},
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Create payment transaction
    payment = PaymentTransaction(
        order_id=payment_request.order_id,
        user_id=user_id,
        payment_method_id=payment_request.payment_method_id,
        amount=payment_request.amount,
        currency=payment_request.currency.upper(),
        description=payment_request.description,
        status=PaymentStatus.PENDING
    )
    
    session.add(payment)
    session.flush()  # Get the payment ID
    
    # Create initial status history entry
    initial_history = PaymentStatusHistory.create_initial_entry(
        payment_id=str(payment.id),
        reason="Payment initiated by user"
    )
    session.add(initial_history)
    
    # Create webhook for payment initiation
    await webhook_simulator.create_payment_webhook(
        payment=payment,
        event_type=WebhookEventType.PAYMENT_INITIATED,
        session=session
    )
    
    session.commit()
    
    # Process payment asynchronously (in background)
    try:
        # Update status to processing
        payment.status = PaymentStatus.PROCESSING
        processing_history = PaymentStatusHistory.create_processing_entry(
            payment_id=str(payment.id)
        )
        session.add(processing_history)
        session.commit()
        
        # Process payment through mock processor
        processing_result = await processor.process_payment(
            payment_id=str(payment.id),
            amount=payment.amount,
            currency=payment.currency,
            payment_method_type=payment_method.type,
            payment_method_details=payment_method.masked_details,
            order_id=str(payment.order_id)
        )
        
        # Update payment with processing result
        if processing_result.success:
            payment.status = PaymentStatus.COMPLETED
            payment.gateway_transaction_id = processing_result.gateway_transaction_id
            payment.processed_at = datetime.utcnow()
            
            # Create completion history entry
            completion_history = PaymentStatusHistory.create_completion_entry(
                payment_id=str(payment.id),
                gateway_transaction_id=processing_result.gateway_transaction_id,
                processing_time_ms=processing_result.processing_time_ms
            )
            session.add(completion_history)
            
            # Create webhook for successful completion
            await webhook_simulator.create_payment_webhook(
                payment=payment,
                event_type=WebhookEventType.PAYMENT_COMPLETED,
                session=session
            )
        else:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = processing_result.failure_reason
            
            # Create failure history entry
            failure_history = PaymentStatusHistory.create_failure_entry(
                payment_id=str(payment.id),
                failure_reason=processing_result.failure_reason,
                error_code=processing_result.error_code,
                gateway_response=processing_result.gateway_response
            )
            session.add(failure_history)
            
            # Create webhook for failure
            await webhook_simulator.create_payment_webhook(
                payment=payment,
                event_type=WebhookEventType.PAYMENT_FAILED,
                session=session
            )
        
        session.commit()
        
    except Exception as e:
        # Handle processing errors
        payment.status = PaymentStatus.FAILED
        payment.failure_reason = f"Processing error: {str(e)}"
        
        failure_history = PaymentStatusHistory.create_failure_entry(
            payment_id=str(payment.id),
            failure_reason=payment.failure_reason,
            error_code="processing_error"
        )
        session.add(failure_history)
        session.commit()
    
    # Return payment response
    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        user_id=payment.user_id,
        payment_method_id=payment.payment_method_id,
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status.value,
        gateway_transaction_id=payment.gateway_transaction_id,
        failure_reason=payment.failure_reason,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
        processed_at=payment.processed_at
    )


@router.get("/payments", response_model=PaymentHistoryResponse)
async def get_payment_history(
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of payments to return"),
    offset: int = Query(default=0, ge=0, description="Number of payments to skip"),
    status: Optional[PaymentStatus] = Query(default=None, description="Filter by payment status"),
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Retrieve payment history for authenticated user.
    
    Returns paginated list of user's payments with optional status filtering.
    """
    # Build query
    query = session.query(PaymentTransaction).filter(
        PaymentTransaction.user_id == user_id
    )
    
    # Apply status filter if provided
    if status:
        query = query.filter(PaymentTransaction.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    payments = query.order_by(
        PaymentTransaction.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    # Convert to response models
    payment_responses = [
        PaymentResponse(
            id=payment.id,
            order_id=payment.order_id,
            user_id=payment.user_id,
            payment_method_id=payment.payment_method_id,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status.value,
            gateway_transaction_id=payment.gateway_transaction_id,
            failure_reason=payment.failure_reason,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
            processed_at=payment.processed_at
        )
        for payment in payments
    ]
    
    return PaymentHistoryResponse(
        payments=payment_responses,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment_details(
    payment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Retrieve details of a specific payment.
    
    Returns detailed information about a payment transaction
    if it belongs to the authenticated user.
    """
    payment = session.query(PaymentTransaction).filter(
        PaymentTransaction.id == payment_id,
        PaymentTransaction.user_id == user_id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Payment not found",
                "code": "payment_not_found",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        user_id=payment.user_id,
        payment_method_id=payment.payment_method_id,
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status.value,
        gateway_transaction_id=payment.gateway_transaction_id,
        failure_reason=payment.failure_reason,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
        processed_at=payment.processed_at
    )


@router.get("/payments/{payment_id}/status", response_model=PaymentStatusResponse)
async def get_payment_status(
    payment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Retrieve current status of a payment.
    
    Returns the current status and last update time for a payment
    if it belongs to the authenticated user.
    """
    payment = session.query(PaymentTransaction).filter(
        PaymentTransaction.id == payment_id,
        PaymentTransaction.user_id == user_id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Payment not found",
                "code": "payment_not_found",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    return PaymentStatusResponse(
        payment_id=payment.id,
        status=payment.status.value,
        updated_at=payment.updated_at
    )
