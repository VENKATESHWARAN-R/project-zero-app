"""
Payment Transaction model for the Payment Processing Service.

This module defines the Payment Transaction entity with complete transaction
lifecycle tracking, status management, and relationships to other entities.
"""

from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Column, String, Integer, DateTime, Text,
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class PaymentStatus(str, Enum):
    """Payment status enumeration following the state machine defined in data-model.md"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class PaymentTransaction(Base):
    """
    Payment Transaction model representing a single payment attempt.
    
    Tracks the complete payment lifecycle from initiation to completion,
    including status changes, failure reasons, and audit trail.
    
    Attributes:
        id: Unique transaction identifier (UUID)
        order_id: Reference to order being paid for (UUID)
        user_id: Reference to user making payment (UUID)
        payment_method_id: Reference to payment method used (UUID)
        amount: Payment amount in cents (to avoid floating point issues)
        currency: Currency code (default: USD)
        status: Current payment status (enum)
        gateway_transaction_id: Mock gateway transaction reference
        failure_reason: Reason for payment failure (optional)
        description: Payment description (optional)
        created_at: Transaction creation timestamp
        updated_at: Last status update timestamp
        processed_at: Payment processing completion timestamp (optional)
    """
    
    __tablename__ = "payment_transactions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # Foreign keys (cross-service references)
    order_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("payment_methods.id"), nullable=False)
    
    # Payment details
    amount = Column(Integer, nullable=False)  # Amount in cents
    currency = Column(String(3), nullable=False, default="USD")
    description = Column(Text, nullable=True)
    
    # Status tracking
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, index=True)
    gateway_transaction_id = Column(String(100), nullable=True)
    failure_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    payment_method = relationship("PaymentMethod", back_populates="transactions")
    status_history = relationship("PaymentStatusHistory", back_populates="payment", cascade="all, delete-orphan")
    webhook_events = relationship("WebhookEvent", back_populates="payment", cascade="all, delete-orphan")
    
    # Indexes for performance optimization
    __table_args__ = (
        Index('idx_payment_order_status', 'order_id', 'status'),
        Index('idx_payment_user_created', 'user_id', 'created_at'),
        Index('idx_payment_status_created', 'status', 'created_at'),
    )
    
    def __init__(self, **kwargs):
        """Initialize payment transaction with validation."""
        super().__init__(**kwargs)
        self._validate_amount()
        self._validate_currency()
    
    def _validate_amount(self):
        """Validate payment amount is positive and non-zero."""
        if self.amount is not None and self.amount <= 0:
            raise ValueError("Payment amount must be positive and greater than 0")
    
    def _validate_currency(self):
        """Validate currency code format."""
        if self.currency and len(self.currency) != 3:
            raise ValueError("Currency must be a valid 3-letter ISO 4217 code")
    
    def can_transition_to(self, new_status: PaymentStatus) -> bool:
        """
        Check if payment can transition to the new status.
        
        Valid transitions based on state machine:
        - PENDING → PROCESSING, CANCELLED
        - PROCESSING → COMPLETED, FAILED
        - COMPLETED → REFUNDED
        - FAILED → PROCESSING (retry)
        - CANCELLED → (no transitions)
        - REFUNDED → (no transitions)
        """
        valid_transitions = {
            PaymentStatus.PENDING: [PaymentStatus.PROCESSING, PaymentStatus.CANCELLED],
            PaymentStatus.PROCESSING: [PaymentStatus.COMPLETED, PaymentStatus.FAILED],
            PaymentStatus.COMPLETED: [PaymentStatus.REFUNDED],
            PaymentStatus.FAILED: [PaymentStatus.PROCESSING],  # Allow retry
            PaymentStatus.CANCELLED: [],  # Terminal state
            PaymentStatus.REFUNDED: [],   # Terminal state
        }
        
        return new_status in valid_transitions.get(self.status, [])
    
    def update_status(self, new_status: PaymentStatus, reason: Optional[str] = None) -> bool:
        """
        Update payment status with validation and timestamp tracking.
        
        Args:
            new_status: New payment status
            reason: Optional reason for status change
            
        Returns:
            bool: True if status was updated, False if transition is invalid
        """
        if not self.can_transition_to(new_status):
            return False
        
        # old_status = self.status  # Keep for potential future use
        self.status = new_status
        self.updated_at = func.now()
        
        # Set processed_at timestamp for terminal states
        if new_status in [PaymentStatus.COMPLETED, PaymentStatus.FAILED, PaymentStatus.CANCELLED]:
            self.processed_at = func.now()
        
        # Create status history entry (will be handled by the service layer)
        return True
    
    def is_terminal_status(self) -> bool:
        """Check if payment is in a terminal status (no further transitions possible)."""
        return self.status in [PaymentStatus.COMPLETED, PaymentStatus.CANCELLED, PaymentStatus.REFUNDED]
    
    def is_successful(self) -> bool:
        """Check if payment completed successfully."""
        return self.status == PaymentStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if payment failed."""
        return self.status == PaymentStatus.FAILED
    
    def to_dict(self) -> dict:
        """Convert payment transaction to dictionary for API responses."""
        return {
            "id": str(self.id),
            "order_id": str(self.order_id),
            "user_id": str(self.user_id),
            "payment_method_id": str(self.payment_method_id),
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status.value,
            "gateway_transaction_id": self.gateway_transaction_id,
            "failure_reason": self.failure_reason,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }
    
    def __repr__(self):
        return f"<PaymentTransaction(id={self.id}, order_id={self.order_id}, status={self.status}, amount={self.amount})>"
