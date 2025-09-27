"""
Payment Method model for the Payment Processing Service.

This module defines the Payment Method entity for storing user payment method
information with secure masking for demonstration purposes.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any
from uuid import uuid4

from sqlalchemy import (
    Column, String, DateTime, Boolean, Index,
    Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class PaymentMethodType(str, Enum):
    """Payment method type enumeration."""
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    PAYPAL = "PAYPAL"


class PaymentMethod(Base):
    """
    Payment Method model for storing user payment method information.
    
    Stores masked payment details for display purposes while maintaining
    security best practices even in mock implementation.
    
    Attributes:
        id: Unique payment method identifier (UUID)
        user_id: Reference to method owner (UUID)
        type: Payment method type (enum)
        display_name: User-friendly name for method
        masked_details: Masked payment details for display (JSON)
        is_default: Whether this is user's default method
        is_active: Whether method is available for use
        expires_at: Expiration date for cards (optional)
        created_at: Method creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "payment_methods"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # Foreign key (cross-service reference)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Payment method details
    type = Column(SQLEnum(PaymentMethodType), nullable=False)
    display_name = Column(String(100), nullable=False)
    masked_details = Column(JSON, nullable=False)
    
    # Status flags
    is_default = Column(Boolean, nullable=False, default=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Expiration (for cards)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    transactions = relationship("PaymentTransaction", back_populates="payment_method")
    
    # Indexes for performance optimization
    __table_args__ = (
        Index('idx_payment_method_user_type', 'user_id', 'type'),
        Index('idx_payment_method_user_default', 'user_id', 'is_default'),
        Index('idx_payment_method_user_active', 'user_id', 'is_active'),
    )
    
    def __init__(self, **kwargs):
        """Initialize payment method with validation."""
        super().__init__(**kwargs)
        self._validate_masked_details()
    
    def _validate_masked_details(self):
        """Validate masked details structure matches payment method type."""
        if not self.masked_details or not isinstance(self.masked_details, dict):
            raise ValueError("Masked details must be a valid dictionary")
        
        if self.type in [PaymentMethodType.CREDIT_CARD, PaymentMethodType.DEBIT_CARD]:
            required_fields = ["last_four", "brand", "exp_month", "exp_year"]
            for field in required_fields:
                if field not in self.masked_details:
                    raise ValueError(f"Credit/Debit card masked details must include {field}")
        
        elif self.type == PaymentMethodType.PAYPAL:
            if "email" not in self.masked_details:
                raise ValueError("PayPal masked details must include email")
    
    @classmethod
    def create_masked_details(cls, payment_type: PaymentMethodType, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create masked details from full payment details.
        
        Args:
            payment_type: Type of payment method
            payment_details: Full payment details (to be masked)
            
        Returns:
            dict: Masked details safe for storage and display
        """
        if payment_type in [PaymentMethodType.CREDIT_CARD, PaymentMethodType.DEBIT_CARD]:
            card_number = payment_details.get("card_number", "")
            return {
                "last_four": card_number[-4:] if len(card_number) >= 4 else "****",
                "brand": cls._detect_card_brand(card_number),
                "exp_month": payment_details.get("exp_month"),
                "exp_year": payment_details.get("exp_year"),
                "cardholder_name": payment_details.get("cardholder_name", "").split()[0] if payment_details.get("cardholder_name") else None
            }
        
        elif payment_type == PaymentMethodType.PAYPAL:
            email = payment_details.get("email", "")
            if "@" in email:
                username, domain = email.split("@", 1)
                masked_username = username[:2] + "*" * (len(username) - 2) if len(username) > 2 else "**"
                return {"email": f"{masked_username}@{domain}"}
            return {"email": "***@***.com"}
        
        return {}
    
    @staticmethod
    def _detect_card_brand(card_number: str) -> str:
        """
        Detect card brand from card number.
        
        Args:
            card_number: Credit card number
            
        Returns:
            str: Card brand (visa, mastercard, amex, discover, etc.)
        """
        if not card_number or not card_number.isdigit():
            return "unknown"
        
        # Remove spaces and hyphens
        card_number = card_number.replace(" ", "").replace("-", "")
        
        # Visa: starts with 4
        if card_number.startswith("4"):
            return "visa"
        
        # Mastercard: starts with 5 or 2221-2720
        if card_number.startswith("5") or (card_number.startswith("2") and 2221 <= int(card_number[:4]) <= 2720):
            return "mastercard"
        
        # American Express: starts with 34 or 37
        if card_number.startswith(("34", "37")):
            return "amex"
        
        # Discover: starts with 6
        if card_number.startswith("6"):
            return "discover"
        
        return "unknown"
    
    def is_expired(self) -> bool:
        """Check if payment method is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def can_be_used(self) -> bool:
        """Check if payment method can be used for new payments."""
        return self.is_active and not self.is_expired()
    
    def set_as_default(self, session):
        """
        Set this payment method as default for the user.
        
        This will unset any other default methods for the same user and type.
        
        Args:
            session: SQLAlchemy session for database operations
        """
        # Unset other default methods for this user and type
        session.query(PaymentMethod).filter(
            PaymentMethod.user_id == self.user_id,
            PaymentMethod.type == self.type,
            PaymentMethod.id != self.id
        ).update({"is_default": False})
        
        # Set this method as default
        self.is_default = True
    
    def deactivate(self):
        """Deactivate payment method (soft delete)."""
        self.is_active = False
        self.is_default = False
        self.updated_at = func.now()
    
    def to_dict(self) -> dict:
        """Convert payment method to dictionary for API responses."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "type": self.type.value,
            "display_name": self.display_name,
            "masked_details": self.masked_details,
            "is_default": self.is_default,
            "is_active": self.is_active,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_display_dict(self) -> dict:
        """Convert payment method to dictionary for display purposes (minimal info)."""
        return {
            "id": str(self.id),
            "type": self.type.value,
            "display_name": self.display_name,
            "masked_details": self.masked_details,
            "is_default": self.is_default,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
    
    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, user_id={self.user_id}, type={self.type}, display_name='{self.display_name}')>"
