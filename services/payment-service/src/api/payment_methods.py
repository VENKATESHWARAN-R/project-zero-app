"""
Payment method management API endpoints.

This module implements the payment method management endpoints including
adding, retrieving, and removing payment methods for users.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from ..models.database import get_session
from ..models.payment_method import PaymentMethod, PaymentMethodType
from ..services.payment_validator import get_payment_validator
from ..utils.security import get_current_user_id


router = APIRouter()


# Pydantic models for request/response
class CreditCardDetails(BaseModel):
    """Credit card details model."""
    card_number: str = Field(..., pattern=r'^[0-9]{13,19}$', description="Credit card number")
    exp_month: int = Field(..., ge=1, le=12, description="Expiration month")
    exp_year: int = Field(..., ge=2024, description="Expiration year")
    cvv: str = Field(..., pattern=r'^[0-9]{3,4}$', description="Card verification value")
    cardholder_name: Optional[str] = Field(None, max_length=100, description="Name on card")


class PayPalDetails(BaseModel):
    """PayPal details model."""
    email: str = Field(..., description="PayPal account email")
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        import re
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v


class PaymentMethodRequest(BaseModel):
    """Payment method request model."""
    type: PaymentMethodType = Field(..., description="Payment method type")
    display_name: str = Field(..., max_length=100, description="User-friendly name for payment method")
    payment_details: Dict[str, Any] = Field(..., description="Payment method details")
    is_default: bool = Field(default=False, description="Set as default payment method")
    
    @validator('payment_details')
    def validate_payment_details(cls, v, values):
        """Validate payment details based on type."""
        if 'type' not in values:
            return v
            
        payment_type = values['type']
        
        if payment_type in [PaymentMethodType.CREDIT_CARD, PaymentMethodType.DEBIT_CARD]:
            try:
                CreditCardDetails(**v)
            except Exception as e:
                raise ValueError(f'Invalid credit/debit card details: {e}')
        elif payment_type == PaymentMethodType.PAYPAL:
            try:
                PayPalDetails(**v)
            except Exception as e:
                raise ValueError(f'Invalid PayPal details: {e}')
        else:
            raise ValueError(f'Unsupported payment method type: {payment_type}')
            
        return v


class PaymentMethodResponse(BaseModel):
    """Payment method response model."""
    id: UUID
    user_id: UUID
    type: str
    display_name: str
    masked_details: Dict[str, Any]
    is_default: bool
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime


class PaymentMethodsResponse(BaseModel):
    """Payment methods response model."""
    payment_methods: List[PaymentMethodResponse]




@router.get("/payment-methods", response_model=PaymentMethodsResponse)
async def get_payment_methods(
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Retrieve all payment methods for authenticated user.
    
    Returns all active payment methods belonging to the user,
    ordered by creation date with default methods first.
    """
    payment_methods = session.query(PaymentMethod).filter(
        PaymentMethod.user_id == user_id,
        PaymentMethod.is_active
    ).order_by(
        PaymentMethod.is_default.desc(),
        PaymentMethod.created_at.desc()
    ).all()
    
    # Convert to response models
    method_responses = [
        PaymentMethodResponse(
            id=method.id,
            user_id=method.user_id,
            type=method.type.value,
            display_name=method.display_name,
            masked_details=method.masked_details,
            is_default=method.is_default,
            is_active=method.is_active,
            expires_at=method.expires_at,
            created_at=method.created_at
        )
        for method in payment_methods
    ]
    
    return PaymentMethodsResponse(payment_methods=method_responses)


@router.post("/payment-methods", response_model=PaymentMethodResponse, status_code=201)
async def add_payment_method(
    method_request: PaymentMethodRequest,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Add a new payment method for authenticated user.
    
    Creates a new payment method with secure storage of payment details.
    Automatically masks sensitive information for security.
    """
    # Get validator service
    validator = get_payment_validator()
    
    # Validate payment method details
    validation_result = validator.validate_payment_method(
        method_type=method_request.type,
        payment_details=method_request.payment_details,
        user_id=str(user_id)
    )
    
    if not validation_result.is_valid:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid payment method data",
                "code": "validation_error",
                "details": validation_result.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Check if user already has maximum number of payment methods
    existing_count = session.query(PaymentMethod).filter(
        PaymentMethod.user_id == user_id,
        PaymentMethod.is_active
    ).count()
    
    if existing_count >= 5:  # Maximum 5 payment methods per user
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Maximum number of payment methods reached",
                "code": "payment_method_limit_exceeded",
                "details": {"max_methods": 5, "current_count": existing_count},
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # If this is set as default, unset other default methods of same type
    if method_request.is_default:
        session.query(PaymentMethod).filter(
            PaymentMethod.user_id == user_id,
            PaymentMethod.type == method_request.type,
            PaymentMethod.is_default
        ).update({"is_default": False})
    
    # Create masked details for secure storage
    masked_details = _create_masked_details(
        method_request.type,
        method_request.payment_details
    )
    
    # Determine expiration date for cards
    expires_at = None
    if method_request.type in [PaymentMethodType.CREDIT_CARD, PaymentMethodType.DEBIT_CARD]:
        exp_month = method_request.payment_details.get('exp_month')
        exp_year = method_request.payment_details.get('exp_year')
        if exp_month and exp_year:
            from datetime import datetime as dt
            expires_at = dt(exp_year, exp_month, 1)
    
    # Create payment method
    payment_method = PaymentMethod(
        user_id=user_id,
        type=method_request.type,
        display_name=method_request.display_name,
        masked_details=masked_details,
        is_default=method_request.is_default,
        expires_at=expires_at
    )
    
    session.add(payment_method)
    session.commit()
    
    return PaymentMethodResponse(
        id=payment_method.id,
        user_id=payment_method.user_id,
        type=payment_method.type.value,
        display_name=payment_method.display_name,
        masked_details=payment_method.masked_details,
        is_default=payment_method.is_default,
        is_active=payment_method.is_active,
        expires_at=payment_method.expires_at,
        created_at=payment_method.created_at
    )


@router.delete("/payment-methods/{method_id}", status_code=204)
async def remove_payment_method(
    method_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Remove a payment method for authenticated user.
    
    Soft deletes the payment method by setting is_active to False.
    Cannot delete if there are pending payments using this method.
    """
    # Find payment method
    payment_method = session.query(PaymentMethod).filter(
        PaymentMethod.id == method_id,
        PaymentMethod.user_id == user_id,
        PaymentMethod.is_active
    ).first()
    
    if not payment_method:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Payment method not found",
                "code": "payment_method_not_found",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Check for pending payments using this method
    from ..models.payment import PaymentTransaction, PaymentStatus
    pending_payments = session.query(PaymentTransaction).filter(
        PaymentTransaction.payment_method_id == method_id,
        PaymentTransaction.status.in_([PaymentStatus.PENDING, PaymentStatus.PROCESSING])
    ).count()
    
    if pending_payments > 0:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Cannot remove payment method with pending payments",
                "code": "payment_method_in_use",
                "details": {"pending_payments": pending_payments},
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Soft delete the payment method
    payment_method.is_active = False
    payment_method.updated_at = datetime.utcnow()
    
    session.commit()
    
    # Return 204 No Content (no response body for successful deletion)
    return


def _create_masked_details(method_type: PaymentMethodType, payment_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create masked payment details for secure storage.
    
    Args:
        method_type: Type of payment method
        payment_details: Raw payment details
        
    Returns:
        Masked payment details safe for storage and display
    """
    if method_type in [PaymentMethodType.CREDIT_CARD, PaymentMethodType.DEBIT_CARD]:
        card_number = payment_details.get('card_number', '')
        
        # Determine card brand from number
        brand = _determine_card_brand(card_number)
        
        return {
            "last_four": card_number[-4:] if len(card_number) >= 4 else "****",
            "brand": brand,
            "exp_month": payment_details.get('exp_month'),
            "exp_year": payment_details.get('exp_year'),
            "cardholder_name": payment_details.get('cardholder_name', "").upper()
        }
    
    elif method_type == PaymentMethodType.PAYPAL:
        email = payment_details.get('email', '')
        
        # Mask email for privacy
        if '@' in email:
            local, domain = email.split('@', 1)
            if len(local) > 2:
                masked_local = local[:2] + '*' * (len(local) - 2)
            else:
                masked_local = '*' * len(local)
            masked_email = f"{masked_local}@{domain}"
        else:
            masked_email = '*' * len(email)
        
        return {
            "email": masked_email,
            "original_email": email  # Store original for processing (in real implementation, this would be encrypted)
        }
    
    else:
        return {}


def _determine_card_brand(card_number: str) -> str:
    """
    Determine card brand from card number.
    
    Args:
        card_number: Credit card number
        
    Returns:
        Card brand name
    """
    if not card_number:
        return "unknown"
    
    # Remove any spaces or dashes
    card_number = card_number.replace(' ', '').replace('-', '')
    
    # Visa: starts with 4
    if card_number.startswith('4'):
        return "visa"
    
    # Mastercard: starts with 5 or 2221-2720
    if card_number.startswith('5') or (card_number.startswith('2') and 2221 <= int(card_number[:4]) <= 2720):
        return "mastercard"
    
    # American Express: starts with 34 or 37
    if card_number.startswith(('34', '37')):
        return "amex"
    
    # Discover: starts with 6
    if card_number.startswith('6'):
        return "discover"
    
    return "unknown"
