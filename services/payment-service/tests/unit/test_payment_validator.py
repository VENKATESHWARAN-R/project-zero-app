"""
Unit tests for the Payment Validator service.

Tests payment validation logic, business rules enforcement,
and comprehensive validation scenarios for all payment types.
"""

import pytest
from datetime import datetime, date
from unittest.mock import patch

from src.services.payment_validator import (
    PaymentValidator,
    ValidationError,
    ValidationResult,
    get_payment_validator
)
from src.models.payment_method import PaymentMethodType


class TestValidationError:
    """Test ValidationError exception class."""
    
    def test_validation_error_creation(self):
        """Test ValidationError creation with all parameters."""
        error = ValidationError(
            message="Invalid card number",
            field="card_number",
            code="invalid_format"
        )
        
        assert error.message == "Invalid card number"
        assert error.field == "card_number"
        assert error.code == "invalid_format"
        assert str(error) == "Invalid card number"
    
    def test_validation_error_minimal(self):
        """Test ValidationError creation with minimal parameters."""
        error = ValidationError("Required field missing")
        
        assert error.message == "Required field missing"
        assert error.field is None
        assert error.code is None


class TestValidationResult:
    """Test ValidationResult class."""
    
    def test_valid_result(self):
        """Test creation of valid result."""
        result = ValidationResult()
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_invalid_result_with_errors(self):
        """Test creation of invalid result with errors."""
        errors = [
            ValidationError("Error 1", "field1", "code1"),
            ValidationError("Error 2", "field2", "code2")
        ]
        result = ValidationResult(is_valid=False, errors=errors)
        
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert result.errors[0].message == "Error 1"
    
    def test_add_error(self):
        """Test adding error to result."""
        result = ValidationResult()
        result.add_error("Test error", "test_field", "test_code")
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].message == "Test error"
        assert result.errors[0].field == "test_field"
        assert result.errors[0].code == "test_code"
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = ValidationResult()
        result.add_error("Test error", "test_field", "test_code")
        
        result_dict = result.to_dict()
        
        assert result_dict["is_valid"] is False
        assert len(result_dict["errors"]) == 1
        assert result_dict["errors"][0]["message"] == "Test error"
        assert result_dict["errors"][0]["field"] == "test_field"
        assert result_dict["errors"][0]["code"] == "test_code"


class TestPaymentValidator:
    """Test PaymentValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = PaymentValidator()
    
    def test_validator_constants(self):
        """Test validator business rule constants."""
        assert self.validator.MIN_PAYMENT_AMOUNT == 50  # $0.50
        assert self.validator.MAX_PAYMENT_AMOUNT == 100000000  # $1,000,000
        assert self.validator.MAX_PAYMENT_METHODS_PER_USER == 5
        assert "USD" in self.validator.SUPPORTED_CURRENCIES
        assert len(self.validator.SUPPORTED_CURRENCIES) >= 4


class TestPaymentAmountValidation:
    """Test payment amount validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = PaymentValidator()
    
    def test_valid_amount(self):
        """Test validation of valid payment amount."""
        result = self.validator.validate_payment_amount(5000)  # $50.00
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_minimum_amount_boundary(self):
        """Test minimum amount boundary validation."""
        # Test exactly at minimum
        result = self.validator.validate_payment_amount(50)
        assert result.is_valid is True
        
        # Test below minimum
        result = self.validator.validate_payment_amount(49)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "at least" in result.errors[0].message
        assert result.errors[0].code == "min_amount"
    
    def test_maximum_amount_boundary(self):
        """Test maximum amount boundary validation."""
        # Test exactly at maximum
        result = self.validator.validate_payment_amount(100000000)
        assert result.is_valid is True
        
        # Test above maximum
        result = self.validator.validate_payment_amount(100000001)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "cannot exceed" in result.errors[0].message
        assert result.errors[0].code == "max_amount"
    
    def test_invalid_amount_type(self):
        """Test validation with invalid amount type."""
        result = self.validator.validate_payment_amount("5000")
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "must be an integer" in result.errors[0].message
        assert result.errors[0].code == "invalid_type"


class TestCurrencyValidation:
    """Test currency validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = PaymentValidator()
    
    def test_valid_currencies(self):
        """Test validation of supported currencies."""
        for currency in ["USD", "EUR", "GBP", "CAD"]:
            result = self.validator.validate_currency(currency)
            assert result.is_valid is True
    
    def test_case_insensitive_currency(self):
        """Test case insensitive currency validation."""
        result = self.validator.validate_currency("usd")
        assert result.is_valid is True
    
    def test_unsupported_currency(self):
        """Test validation of unsupported currency."""
        result = self.validator.validate_currency("XYZ")
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "not supported" in result.errors[0].message
        assert result.errors[0].code == "unsupported_currency"
    
    def test_empty_currency(self):
        """Test validation of empty currency."""
        result = self.validator.validate_currency("")
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "required"
    
    def test_invalid_currency_format(self):
        """Test validation of invalid currency format."""
        result = self.validator.validate_currency("US")  # Too short
        
        assert result.is_valid is False
        assert "3-letter code" in result.errors[0].message
        assert result.errors[0].code == "invalid_format"


class TestCreditCardValidation:
    """Test credit card validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = PaymentValidator()
    
    def test_valid_credit_card(self):
        """Test validation of valid credit card."""
        card_details = {
            "card_number": "4111111111111111",  # Valid Visa test number
            "exp_month": 12,
            "exp_year": 2025,
            "cvv": "123",
            "cardholder_name": "John Doe"
        }
        
        result = self.validator.validate_payment_method(
            PaymentMethodType.CREDIT_CARD,
            "My Visa Card",
            card_details
        )
        
        assert result.is_valid is True
    
    def test_invalid_card_number_format(self):
        """Test validation of invalid card number format."""
        card_details = {
            "card_number": "411111111111111",  # Too short
            "exp_month": 12,
            "exp_year": 2025,
            "cvv": "123"
        }
        
        result = self.validator._validate_credit_card(card_details)
        
        assert result.is_valid is False
        assert any("13-19 digits" in error.message for error in result.errors)
    
    def test_invalid_card_number_luhn(self):
        """Test validation with invalid Luhn checksum."""
        card_details = {
            "card_number": "4111111111111112",  # Invalid checksum
            "exp_month": 12,
            "exp_year": 2025,
            "cvv": "123"
        }
        
        result = self.validator._validate_credit_card(card_details)
        
        assert result.is_valid is False
        assert any("invalid" in error.message.lower() for error in result.errors)
    
    def test_expired_card(self):
        """Test validation of expired card."""
        card_details = {
            "card_number": "4111111111111111",
            "exp_month": 1,
            "exp_year": 2020,  # Expired
            "cvv": "123"
        }
        
        result = self.validator._validate_credit_card(card_details)
        
        assert result.is_valid is False
        assert any("expired" in error.message.lower() for error in result.errors)
    
    def test_invalid_cvv(self):
        """Test validation of invalid CVV."""
        card_details = {
            "card_number": "4111111111111111",
            "exp_month": 12,
            "exp_year": 2025,
            "cvv": "12"  # Too short
        }
        
        result = self.validator._validate_credit_card(card_details)
        
        assert result.is_valid is False
        assert any("3-4 digits" in error.message for error in result.errors)
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        card_details = {
            "card_number": "4111111111111111",
            # Missing exp_month, exp_year, cvv
        }
        
        result = self.validator._validate_credit_card(card_details)
        
        assert result.is_valid is False
        assert len(result.errors) >= 3  # Missing fields


class TestPayPalValidation:
    """Test PayPal validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = PaymentValidator()
    
    def test_valid_paypal(self):
        """Test validation of valid PayPal details."""
        paypal_details = {
            "email": "user@example.com"
        }
        
        result = self.validator._validate_paypal(paypal_details)
        
        assert result.is_valid is True
    
    def test_invalid_email_format(self):
        """Test validation of invalid email format."""
        paypal_details = {
            "email": "invalid-email"
        }
        
        result = self.validator._validate_paypal(paypal_details)
        
        assert result.is_valid is False
        assert any("Invalid email format" in error.message for error in result.errors)
    
    def test_missing_email(self):
        """Test validation with missing email."""
        paypal_details = {}
        
        result = self.validator._validate_paypal(paypal_details)
        
        assert result.is_valid is False
        assert any("required" in error.message.lower() for error in result.errors)


class TestPaymentRequestValidation:
    """Test complete payment request validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = PaymentValidator()
    
    def test_valid_payment_request(self):
        """Test validation of complete valid payment request."""
        result = self.validator.validate_payment_request(
            amount=5000,
            currency="USD",
            order_id="550e8400-e29b-41d4-a716-446655440000",
            payment_method_id="550e8400-e29b-41d4-a716-446655440001",
            user_id="550e8400-e29b-41d4-a716-446655440002",
            description="Test payment"
        )
        
        assert result.is_valid is True
    
    def test_invalid_uuid_format(self):
        """Test validation with invalid UUID format."""
        result = self.validator.validate_payment_request(
            amount=5000,
            currency="USD",
            order_id="invalid-uuid",
            payment_method_id="550e8400-e29b-41d4-a716-446655440001",
            user_id="550e8400-e29b-41d4-a716-446655440002"
        )
        
        assert result.is_valid is False
        assert any("valid UUID" in error.message for error in result.errors)
    
    def test_description_too_long(self):
        """Test validation with description too long."""
        long_description = "x" * 256  # Exceeds 255 character limit
        
        result = self.validator.validate_payment_request(
            amount=5000,
            currency="USD",
            order_id="550e8400-e29b-41d4-a716-446655440000",
            payment_method_id="550e8400-e29b-41d4-a716-446655440001",
            user_id="550e8400-e29b-41d4-a716-446655440002",
            description=long_description
        )
        
        assert result.is_valid is False
        assert any("255 characters" in error.message for error in result.errors)


class TestLuhnValidation:
    """Test Luhn algorithm validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = PaymentValidator()
    
    def test_valid_luhn_numbers(self):
        """Test validation of valid Luhn numbers."""
        valid_numbers = [
            "4111111111111111",  # Visa
            "5555555555554444",  # Mastercard
            "378282246310005",   # American Express
            "6011111111111117",  # Discover
        ]
        
        for number in valid_numbers:
            assert self.validator._validate_luhn(number) is True
    
    def test_invalid_luhn_numbers(self):
        """Test validation of invalid Luhn numbers."""
        invalid_numbers = [
            "4111111111111112",  # Invalid checksum
            "5555555555554445",  # Invalid checksum
            "1234567890123456",  # Invalid checksum
        ]
        
        for number in invalid_numbers:
            assert self.validator._validate_luhn(number) is False


class TestValidatorSingleton:
    """Test validator singleton functionality."""
    
    def test_singleton_instance(self):
        """Test that get_payment_validator returns singleton instance."""
        validator1 = get_payment_validator()
        validator2 = get_payment_validator()
        
        assert validator1 is validator2
        assert isinstance(validator1, PaymentValidator)
