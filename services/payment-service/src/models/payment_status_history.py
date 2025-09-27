"""
Payment Status History model for the Payment Processing Service.

This module defines the Payment Status History entity for maintaining
a complete audit trail of all payment status changes.
"""

from typing import Dict, Any, Optional
from uuid import uuid4

from sqlalchemy import (
    Column, String, DateTime, Text, ForeignKey, 
    Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .payment import PaymentStatus

Base = declarative_base()


class PaymentStatusHistory(Base):
    """
    Payment Status History model for audit trail of payment status changes.
    
    Maintains a complete, immutable record of all payment status transitions
    for compliance, debugging, and audit purposes.
    
    Attributes:
        id: Unique history entry identifier (UUID)
        payment_id: Reference to payment transaction (UUID)
        previous_status: Status before change (enum)
        new_status: Status after change (enum)
        reason: Reason for status change (optional)
        context_data: Additional context data (JSON, optional)
        created_at: Status change timestamp
        created_by: System or user that triggered change
    """
    
    __tablename__ = "payment_status_history"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # Foreign key
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payment_transactions.id"), nullable=False, index=True)
    
    # Status change details
    previous_status = Column(SQLEnum(PaymentStatus), nullable=True)  # Null for initial status
    new_status = Column(SQLEnum(PaymentStatus), nullable=False)
    reason = Column(Text, nullable=True)
    context_data = Column(JSON, nullable=True)
    
    # Audit information
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    created_by = Column(String(100), nullable=False, default="system")
    
    # Relationships
    payment = relationship("PaymentTransaction", back_populates="status_history")
    
    # Indexes for performance optimization
    __table_args__ = (
        Index('idx_status_history_payment_created', 'payment_id', 'created_at'),
        Index('idx_status_history_status_created', 'new_status', 'created_at'),
    )
    
    def __init__(self, **kwargs):
        """Initialize payment status history entry with validation."""
        super().__init__(**kwargs)
        self._validate_status_transition()
        self._validate_context_data()
    
    def _validate_status_transition(self):
        """Validate that the status transition is logical."""
        # Allow any transition for flexibility, but log unusual ones
        if self.previous_status == self.new_status:
            raise ValueError("Previous status and new status cannot be the same")
    
    def _validate_context_data(self):
        """Validate context_data is valid JSON if provided."""
        if self.context_data is not None and not isinstance(self.context_data, dict):
            raise ValueError("Context data must be a valid dictionary")
    
    @classmethod
    def create_entry(
        cls,
        payment_id: str,
        previous_status: Optional[PaymentStatus],
        new_status: PaymentStatus,
        reason: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None,
        created_by: str = "system"
    ) -> "PaymentStatusHistory":
        """
        Create a new status history entry.
        
        Args:
            payment_id: Payment transaction ID
            previous_status: Previous payment status (None for initial)
            new_status: New payment status
            reason: Optional reason for the change
            context_data: Optional additional context data
            created_by: Who/what triggered the change
            
        Returns:
            PaymentStatusHistory: New history entry
        """
        return cls(
            payment_id=payment_id,
            previous_status=previous_status,
            new_status=new_status,
            reason=reason,
            context_data=context_data or {},
            created_by=created_by
        )
    
    @classmethod
    def create_initial_entry(
        cls,
        payment_id: str,
        initial_status: PaymentStatus = PaymentStatus.PENDING,
        reason: str = "Payment initiated",
        created_by: str = "system"
    ) -> "PaymentStatusHistory":
        """
        Create initial status history entry for new payment.
        
        Args:
            payment_id: Payment transaction ID
            initial_status: Initial payment status
            reason: Reason for payment creation
            created_by: Who created the payment
            
        Returns:
            PaymentStatusHistory: Initial history entry
        """
        return cls.create_entry(
            payment_id=payment_id,
            previous_status=None,
            new_status=initial_status,
            reason=reason,
            context_data={"initial_entry": True},
            created_by=created_by
        )
    
    @classmethod
    def create_processing_entry(
        cls,
        payment_id: str,
        gateway_info: Optional[Dict[str, Any]] = None,
        created_by: str = "payment_processor"
    ) -> "PaymentStatusHistory":
        """
        Create status history entry for payment processing start.
        
        Args:
            payment_id: Payment transaction ID
            gateway_info: Optional gateway processing information
            created_by: Processing system identifier
            
        Returns:
            PaymentStatusHistory: Processing history entry
        """
        context_metadata = {"processing_started": True}
        if gateway_info:
            context_metadata.update(gateway_info)
        
        return cls.create_entry(
            payment_id=payment_id,
            previous_status=PaymentStatus.PENDING,
            new_status=PaymentStatus.PROCESSING,
            reason="Payment processing started",
            context_data=context_metadata,
            created_by=created_by
        )
    
    @classmethod
    def create_completion_entry(
        cls,
        payment_id: str,
        gateway_transaction_id: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        created_by: str = "payment_processor"
    ) -> "PaymentStatusHistory":
        """
        Create status history entry for successful payment completion.
        
        Args:
            payment_id: Payment transaction ID
            gateway_transaction_id: Gateway transaction reference
            processing_time_ms: Processing time in milliseconds
            created_by: Processing system identifier
            
        Returns:
            PaymentStatusHistory: Completion history entry
        """
        context_metadata = {"payment_completed": True}
        if gateway_transaction_id:
            context_metadata["gateway_transaction_id"] = gateway_transaction_id
        if processing_time_ms:
            context_metadata["processing_time_ms"] = processing_time_ms
        
        return cls.create_entry(
            payment_id=payment_id,
            previous_status=PaymentStatus.PROCESSING,
            new_status=PaymentStatus.COMPLETED,
            reason="Payment processed successfully",
            context_data=context_metadata,
            created_by=created_by
        )
    
    @classmethod
    def create_failure_entry(
        cls,
        payment_id: str,
        failure_reason: str,
        error_code: Optional[str] = None,
        gateway_response: Optional[Dict[str, Any]] = None,
        created_by: str = "payment_processor"
    ) -> "PaymentStatusHistory":
        """
        Create status history entry for payment failure.
        
        Args:
            payment_id: Payment transaction ID
            failure_reason: Human-readable failure reason
            error_code: Machine-readable error code
            gateway_response: Full gateway response data
            created_by: Processing system identifier
            
        Returns:
            PaymentStatusHistory: Failure history entry
        """
        context_metadata = {
            "payment_failed": True,
            "failure_reason": failure_reason
        }
        if error_code:
            context_metadata["error_code"] = error_code
        if gateway_response:
            context_metadata["gateway_response"] = gateway_response
        
        return cls.create_entry(
            payment_id=payment_id,
            previous_status=PaymentStatus.PROCESSING,
            new_status=PaymentStatus.FAILED,
            reason=failure_reason,
            context_data=context_metadata,
            created_by=created_by
        )
    
    @classmethod
    def create_cancellation_entry(
        cls,
        payment_id: str,
        cancellation_reason: str = "Payment cancelled by user",
        cancelled_by: str = "user",
        created_by: str = "system"
    ) -> "PaymentStatusHistory":
        """
        Create status history entry for payment cancellation.
        
        Args:
            payment_id: Payment transaction ID
            cancellation_reason: Reason for cancellation
            cancelled_by: Who cancelled the payment
            created_by: System that processed the cancellation
            
        Returns:
            PaymentStatusHistory: Cancellation history entry
        """
        context_metadata = {
            "payment_cancelled": True,
            "cancelled_by": cancelled_by
        }
        
        return cls.create_entry(
            payment_id=payment_id,
            previous_status=PaymentStatus.PENDING,  # Can be cancelled from PENDING
            new_status=PaymentStatus.CANCELLED,
            reason=cancellation_reason,
            context_data=context_metadata,
            created_by=created_by
        )
    
    def is_terminal_transition(self) -> bool:
        """Check if this transition moved payment to a terminal state."""
        terminal_statuses = [PaymentStatus.COMPLETED, PaymentStatus.CANCELLED, PaymentStatus.REFUNDED]
        return self.new_status in terminal_statuses
    
    def is_failure_transition(self) -> bool:
        """Check if this transition represents a payment failure."""
        return self.new_status == PaymentStatus.FAILED
    
    def is_success_transition(self) -> bool:
        """Check if this transition represents a successful payment."""
        return self.new_status == PaymentStatus.COMPLETED
    
    def get_transition_duration(self, previous_entry: Optional["PaymentStatusHistory"] = None) -> Optional[float]:
        """
        Calculate duration between this transition and the previous one.
        
        Args:
            previous_entry: Previous status history entry
            
        Returns:
            float: Duration in seconds, or None if no previous entry
        """
        if not previous_entry:
            return None
        
        duration = (self.created_at - previous_entry.created_at).total_seconds()
        return duration
    
    def to_dict(self) -> dict:
        """Convert status history entry to dictionary for API responses."""
        return {
            "id": str(self.id),
            "payment_id": str(self.payment_id),
            "previous_status": self.previous_status.value if self.previous_status else None,
            "new_status": self.new_status.value,
            "reason": self.reason,
            "context_data": self.context_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
        }
    
    def __repr__(self):
        return f"<PaymentStatusHistory(id={self.id}, payment_id={self.payment_id}, {self.previous_status} → {self.new_status})>"
