"""
Payment Validation Service for the Payment Processing Service.

This module provides comprehensive validation for payment requests,
payment methods, and business rules enforcement.
"""

import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

from ..models.payment_method import PaymentMethodType


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, code: Optional[str] = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)


class ValidationResult:
    """Result of validation operation."""
    
    def __init__(self, is_valid: bool = True, errors: Optional[List[ValidationError]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, message: str, field: Optional[str] = None, code: Optional[str] = None):
        """Add validation error."""
        self.errors.append(ValidationError(message, field, code))
        self.is_valid = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "is_valid": self.is_valid,
            "errors": [
                {
                    "message": error.message,
                    "field": error.field,
                    "code": error.code
                }
                for error in self.errors
            ]
        }


class PaymentValidator:
    """
    Comprehensive payment validation service.
    
    Validates payment requests, payment methods, amounts, and enforces
    business rules for the payment processing system.
    """
    
    # Business rule constants
    MIN_PAYMENT_AMOUNT = 50  # $0.50 in cents
    MAX_PAYMENT_AMOUNT = 100000000  # $1,000,000 in cents
    MAX_PAYMENT_METHODS_PER_USER = 5
    SUPPORTED_CURRENCIES = {"USD", "EUR", "GBP", "CAD"}
    
    # Card validation patterns
    CARD_NUMBER_PATTERN = re.compile(r'^[0-9]{13,19}$')
    CVV_PATTERN = re.compile(r'^[0-9]{3,4}$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def __init__(self):
        self.card_validators = {
            PaymentMethodType.CREDIT_CARD: self._validate_credit_card,
            PaymentMethodType.DEBIT_CARD: self._validate_debit_card,
            PaymentMethodType.PAYPAL: self._validate_paypal,
        }
    
    def validate_payment_request(
        self,
        amount: int,
        currency: str,
        order_id: str,
        payment_method_id: str,
        user_id: str,
        description: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate a payment request.
        
        Args:
            amount: Payment amount in cents
            currency: Currency code
            order_id: Order identifier
            payment_method_id: Payment method identifier
            user_id: User identifier
            description: Optional payment description
            
        Returns:
            ValidationResult: Validation result with errors if any
        """
        result = ValidationResult()
        
        # Validate amount
        amount_validation = self.validate_payment_amount(amount)
        if not amount_validation.is_valid:
            result.errors.extend(amount_validation.errors)
            result.is_valid = False
        
        # Validate currency
        currency_validation = self.validate_currency(currency)
        if not currency_validation.is_valid:
            result.errors.extend(currency_validation.errors)
            result.is_valid = False
        
        # Validate required fields
        if not order_id or not order_id.strip():
            result.add_error("Order ID is required", "order_id", "required")
        
        if not payment_method_id or not payment_method_id.strip():
            result.add_error("Payment method ID is required", "payment_method_id", "required")
        
        if not user_id or not user_id.strip():
            result.add_error("User ID is required", "user_id", "required")
        
        # Validate UUID format for IDs
        if order_id and not self._is_valid_uuid(order_id):
            result.add_error("Order ID must be a valid UUID", "order_id", "invalid_format")
        
        if payment_method_id and not self._is_valid_uuid(payment_method_id):
            result.add_error("Payment method ID must be a valid UUID", "payment_method_id", "invalid_format")
        
        if user_id and not self._is_valid_uuid(user_id):
            result.add_error("User ID must be a valid UUID", "user_id", "invalid_format")
        
        # Validate description length
        if description and len(description) > 255:
            result.add_error("Description must be 255 characters or less", "description", "max_length")
        
        return result
    
    def validate_payment_amount(self, amount: int) -> ValidationResult:
        """
        Validate payment amount.
        
        Args:
            amount: Payment amount in cents
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()
        
        if not isinstance(amount, int):
            result.add_error("Amount must be an integer", "amount", "invalid_type")
            return result
        
        if amount < self.MIN_PAYMENT_AMOUNT:
            result.add_error(
                f"Amount must be at least ${self.MIN_PAYMENT_AMOUNT / 100:.2f}",
                "amount",
                "min_amount"
            )
        
        if amount > self.MAX_PAYMENT_AMOUNT:
            result.add_error(
                f"Amount cannot exceed ${self.MAX_PAYMENT_AMOUNT / 100:,.2f}",
                "amount",
                "max_amount"
            )
        
        return result
    
    def validate_currency(self, currency: str) -> ValidationResult:
        """
        Validate currency code.
        
        Args:
            currency: Currency code (e.g., "USD")
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()
        
        if not currency:
            result.add_error("Currency is required", "currency", "required")
            return result
        
        if not isinstance(currency, str):
            result.add_error("Currency must be a string", "currency", "invalid_type")
            return result
        
        currency = currency.upper()
        
        if len(currency) != 3:
            result.add_error("Currency must be a 3-letter code", "currency", "invalid_format")
        
        if currency not in self.SUPPORTED_CURRENCIES:
            result.add_error(
                f"Currency '{currency}' is not supported. Supported currencies: {', '.join(self.SUPPORTED_CURRENCIES)}",
                "currency",
                "unsupported_currency"
            )
        
        return result
    
    def validate_payment_method(
        self,
        payment_type: PaymentMethodType,
        display_name: str,
        payment_details: Dict[str, Any],
        user_payment_method_count: int = 0
    ) -> ValidationResult:
        """
        Validate payment method data.
        
        Args:
            payment_type: Type of payment method
            display_name: User-friendly name
            payment_details: Payment method details
            user_payment_method_count: Current number of user's payment methods
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()
        
        # Validate display name
        if not display_name or not display_name.strip():
            result.add_error("Display name is required", "display_name", "required")
        elif len(display_name.strip()) > 100:
            result.add_error("Display name must be 100 characters or less", "display_name", "max_length")
        
        # Validate payment method limit
        if user_payment_method_count >= self.MAX_PAYMENT_METHODS_PER_USER:
            result.add_error(
                f"Maximum {self.MAX_PAYMENT_METHODS_PER_USER} payment methods allowed per user",
                "payment_methods",
                "max_limit"
            )
        
        # Validate payment details based on type
        if payment_type in self.card_validators:
            details_validation = self.card_validators[payment_type](payment_details)
            if not details_validation.is_valid:
                result.errors.extend(details_validation.errors)
                result.is_valid = False
        else:
            result.add_error(f"Unsupported payment method type: {payment_type}", "type", "unsupported_type")
        
        return result
    
    def _validate_credit_card(self, details: Dict[str, Any]) -> ValidationResult:
        """Validate credit card details."""
        return self._validate_card_details(details, "credit card")
    
    def _validate_debit_card(self, details: Dict[str, Any]) -> ValidationResult:
        """Validate debit card details."""
        return self._validate_card_details(details, "debit card")
    
    def _validate_card_details(self, details: Dict[str, Any], card_type: str) -> ValidationResult:
        """Validate card details (credit or debit)."""
        result = ValidationResult()
        
        # Required fields
        required_fields = ["card_number", "exp_month", "exp_year", "cvv"]
        for field in required_fields:
            if field not in details or not details[field]:
                result.add_error(f"{field.replace('_', ' ').title()} is required", field, "required")
        
        # Validate card number
        card_number = str(details.get("card_number", "")).replace(" ", "").replace("-", "")
        if card_number:
            if not self.CARD_NUMBER_PATTERN.match(card_number):
                result.add_error("Card number must be 13-19 digits", "card_number", "invalid_format")
            elif not self._validate_luhn(card_number):
                result.add_error("Card number is invalid", "card_number", "invalid_checksum")
        
        # Validate expiration month
        exp_month = details.get("exp_month")
        if exp_month is not None:
            try:
                month = int(exp_month)
                if month < 1 or month > 12:
                    result.add_error("Expiration month must be between 1 and 12", "exp_month", "invalid_range")
            except (ValueError, TypeError):
                result.add_error("Expiration month must be a number", "exp_month", "invalid_type")
        
        # Validate expiration year
        exp_year = details.get("exp_year")
        if exp_year is not None:
            try:
                year = int(exp_year)
                current_year = datetime.now().year
                if year < current_year:
                    result.add_error("Card has expired", "exp_year", "expired")
                elif year > current_year + 20:
                    result.add_error("Expiration year is too far in the future", "exp_year", "invalid_range")
            except (ValueError, TypeError):
                result.add_error("Expiration year must be a number", "exp_year", "invalid_type")
        
        # Validate CVV
        cvv = str(details.get("cvv", ""))
        if cvv and not self.CVV_PATTERN.match(cvv):
            result.add_error("CVV must be 3-4 digits", "cvv", "invalid_format")
        
        # Validate cardholder name (optional)
        cardholder_name = details.get("cardholder_name")
        if cardholder_name and len(cardholder_name) > 100:
            result.add_error("Cardholder name must be 100 characters or less", "cardholder_name", "max_length")
        
        return result
    
    def _validate_paypal(self, details: Dict[str, Any]) -> ValidationResult:
        """Validate PayPal details."""
        result = ValidationResult()
        
        # Required fields
        if "email" not in details or not details["email"]:
            result.add_error("Email is required for PayPal", "email", "required")
            return result
        
        email = details["email"].strip()
        
        # Validate email format
        if not self.EMAIL_PATTERN.match(email):
            result.add_error("Invalid email format", "email", "invalid_format")
        
        # Validate email length
        if len(email) > 254:
            result.add_error("Email must be 254 characters or less", "email", "max_length")
        
        return result
    
    def _validate_luhn(self, card_number: str) -> bool:
        """
        Validate card number using Luhn algorithm.
        
        Args:
            card_number: Card number string
            
        Returns:
            bool: True if valid, False otherwise
        """
        def luhn_checksum(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10
        
        try:
            return luhn_checksum(card_number) == 0
        except (ValueError, TypeError):
            return False
    
    def _is_valid_uuid(self, uuid_string: str) -> bool:
        """
        Validate UUID format.
        
        Args:
            uuid_string: UUID string to validate
            
        Returns:
            bool: True if valid UUID format
        """
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        return bool(uuid_pattern.match(uuid_string))
    
    def validate_card_expiration(self, exp_month: int, exp_year: int) -> ValidationResult:
        """
        Validate card expiration date.
        
        Args:
            exp_month: Expiration month (1-12)
            exp_year: Expiration year (4 digits)
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()
        
        try:
            # Create date for last day of expiration month
            if exp_month == 12:
                next_month = 1
                next_year = exp_year + 1
            else:
                next_month = exp_month + 1
                next_year = exp_year
            
            # Card expires at end of the month
            exp_date = date(next_year, next_month, 1)
            current_date = date.today()
            
            if exp_date <= current_date:
                result.add_error("Card has expired", "expiration", "expired")
        
        except ValueError:
            result.add_error("Invalid expiration date", "expiration", "invalid_date")
        
        return result
    
    def validate_daily_limit(
        self,
        user_id: str,
        amount: int,
        daily_spent_amount: int,
        daily_limit: int = 500000  # $5,000 default daily limit
    ) -> ValidationResult:
        """
        Validate daily spending limit.
        
        Args:
            user_id: User identifier
            amount: Payment amount in cents
            daily_spent_amount: Amount already spent today in cents
            daily_limit: Daily spending limit in cents
            
        Returns:
            ValidationResult: Validation result
        """
        result = ValidationResult()
        
        total_amount = daily_spent_amount + amount
        
        if total_amount > daily_limit:
            remaining = daily_limit - daily_spent_amount
            result.add_error(
                f"Daily spending limit exceeded. Remaining limit: ${remaining / 100:.2f}",
                "amount",
                "daily_limit_exceeded"
            )
        
        return result


# Global validator instance
_validator_instance: Optional[PaymentValidator] = None


def get_payment_validator() -> PaymentValidator:
    """Get singleton payment validator instance."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = PaymentValidator()
    return _validator_instance
