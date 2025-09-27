"""
Mock Payment Processor for the Payment Processing Service.

This module provides realistic payment processing simulation with configurable
success rates, processing delays, and comprehensive failure scenarios.
"""

import asyncio
import os
import random
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, Tuple

from ..models.payment import PaymentStatus
from ..models.payment_method import PaymentMethodType


class PaymentGateway(str, Enum):
    """Mock payment gateway types."""
    STRIPE_MOCK = "stripe_mock"
    PAYPAL_MOCK = "paypal_mock"
    SQUARE_MOCK = "square_mock"


class PaymentFailureReason(str, Enum):
    """Payment failure reason enumeration."""
    INSUFFICIENT_FUNDS = "insufficient_funds"
    CARD_DECLINED = "card_declined"
    NETWORK_ERROR = "network_error"
    INVALID_PAYMENT_METHOD = "invalid_payment_method"
    EXPIRED_CARD = "expired_card"
    FRAUD_DETECTED = "fraud_detected"
    GATEWAY_ERROR = "gateway_error"


class PaymentProcessorConfig:
    """Configuration for payment processor behavior."""
    
    def __init__(self):
        # Success rate (0.0 to 1.0)
        self.success_rate = float(os.getenv("PAYMENT_SUCCESS_RATE", "0.95"))
        
        # Processing delays in milliseconds
        self.processing_delay_min = int(os.getenv("PAYMENT_PROCESSING_DELAY_MIN", "1000"))
        self.processing_delay_max = int(os.getenv("PAYMENT_PROCESSING_DELAY_MAX", "3000"))
        
        # Enable/disable failure scenarios
        self.failure_scenarios_enabled = os.getenv("PAYMENT_FAILURE_SCENARIOS", "true").lower() == "true"
        
        # Failure distribution (percentages of failures)
        self.failure_distribution = {
            PaymentFailureReason.INSUFFICIENT_FUNDS: 0.10,  # 10% of failures
            PaymentFailureReason.CARD_DECLINED: 0.60,       # 60% of failures
            PaymentFailureReason.NETWORK_ERROR: 0.20,       # 20% of failures
            PaymentFailureReason.INVALID_PAYMENT_METHOD: 0.10,  # 10% of failures
        }
        
        # Gateway selection weights
        self.gateway_weights = {
            PaymentGateway.STRIPE_MOCK: 0.7,   # 70% of transactions
            PaymentGateway.PAYPAL_MOCK: 0.2,   # 20% of transactions
            PaymentGateway.SQUARE_MOCK: 0.1,   # 10% of transactions
        }


class PaymentResult:
    """Result of payment processing attempt."""
    
    def __init__(
        self,
        success: bool,
        status: PaymentStatus,
        gateway_transaction_id: Optional[str] = None,
        failure_reason: Optional[str] = None,
        error_code: Optional[str] = None,
        gateway: Optional[PaymentGateway] = None,
        processing_time_ms: Optional[int] = None,
        gateway_response: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.status = status
        self.gateway_transaction_id = gateway_transaction_id
        self.failure_reason = failure_reason
        self.error_code = error_code
        self.gateway = gateway
        self.processing_time_ms = processing_time_ms
        self.gateway_response = gateway_response or {}
        self.processed_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "status": self.status.value,
            "gateway_transaction_id": self.gateway_transaction_id,
            "failure_reason": self.failure_reason,
            "error_code": self.error_code,
            "gateway": self.gateway.value if self.gateway else None,
            "processing_time_ms": self.processing_time_ms,
            "gateway_response": self.gateway_response,
            "processed_at": self.processed_at.isoformat(),
        }


class MockPaymentProcessor:
    """
    Mock payment processor with realistic simulation features.
    
    Provides configurable success rates, processing delays, and failure scenarios
    to simulate real-world payment processing behavior.
    """
    
    def __init__(self, config: Optional[PaymentProcessorConfig] = None):
        self.config = config or PaymentProcessorConfig()
        self._transaction_counter = 0
    
    async def process_payment(
        self,
        payment_id: str,
        amount: int,
        currency: str,
        payment_method_type: PaymentMethodType,
        payment_method_details: Dict[str, Any],
        order_id: Optional[str] = None
    ) -> PaymentResult:
        """
        Process a payment with realistic simulation.
        
        Args:
            payment_id: Unique payment identifier
            amount: Payment amount in cents
            currency: Currency code (e.g., "USD")
            payment_method_type: Type of payment method
            payment_method_details: Payment method details
            order_id: Optional order identifier
            
        Returns:
            PaymentResult: Result of payment processing
        """
        start_time = datetime.utcnow()
        
        # Simulate processing delay
        await self._simulate_processing_delay()
        
        # Select gateway based on payment method
        gateway = self._select_gateway(payment_method_type)
        
        # Check for forced failure scenarios (for testing)
        forced_result = self._check_forced_scenarios(amount)
        if forced_result:
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            forced_result.processing_time_ms = processing_time
            forced_result.gateway = gateway
            return forced_result
        
        # Determine if payment should succeed or fail
        should_succeed = random.random() < self.config.success_rate
        
        if should_succeed:
            result = await self._process_successful_payment(
                payment_id, amount, currency, gateway, payment_method_type
            )
        else:
            result = await self._process_failed_payment(
                payment_id, amount, currency, gateway, payment_method_type
            )
        
        # Calculate processing time
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        result.processing_time_ms = processing_time
        
        return result
    
    async def _simulate_processing_delay(self):
        """Simulate realistic processing delay."""
        delay_ms = random.randint(
            self.config.processing_delay_min,
            self.config.processing_delay_max
        )
        await asyncio.sleep(delay_ms / 1000.0)
    
    def _select_gateway(self, payment_method_type: PaymentMethodType) -> PaymentGateway:
        """Select payment gateway based on payment method type and weights."""
        if payment_method_type == PaymentMethodType.PAYPAL:
            return PaymentGateway.PAYPAL_MOCK
        
        # For credit/debit cards, use weighted selection
        gateways = list(self.config.gateway_weights.keys())
        weights = list(self.config.gateway_weights.values())
        
        # Filter out PayPal for card payments
        card_gateways = [g for g in gateways if g != PaymentGateway.PAYPAL_MOCK]
        card_weights = [self.config.gateway_weights[g] for g in card_gateways]
        
        # Normalize weights
        total_weight = sum(card_weights)
        normalized_weights = [w / total_weight for w in card_weights]
        
        return random.choices(card_gateways, weights=normalized_weights)[0]
    
    def _check_forced_scenarios(self, amount: int) -> Optional[PaymentResult]:
        """
        Check for forced failure scenarios based on amount.
        
        Special amounts for testing:
        - Amount ending in 01: Insufficient funds
        - Amount ending in 02: Card declined
        - Amount ending in 03: Network error
        - Amount ending in 04: Invalid payment method
        """
        if not self.config.failure_scenarios_enabled:
            return None
        
        last_two_digits = amount % 100
        
        if last_two_digits == 1:
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                failure_reason="Insufficient funds",
                error_code="insufficient_funds",
                gateway_response={"error": "Insufficient funds in account"}
            )
        elif last_two_digits == 2:
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                failure_reason="Card declined by issuer",
                error_code="card_declined",
                gateway_response={"error": "Card declined", "decline_code": "generic_decline"}
            )
        elif last_two_digits == 3:
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                failure_reason="Network error during processing",
                error_code="network_error",
                gateway_response={"error": "Network timeout", "retry_after": 30}
            )
        elif last_two_digits == 4:
            return PaymentResult(
                success=False,
                status=PaymentStatus.FAILED,
                failure_reason="Invalid payment method",
                error_code="invalid_payment_method",
                gateway_response={"error": "Payment method not supported"}
            )
        
        return None
    
    async def _process_successful_payment(
        self,
        payment_id: str,
        amount: int,
        currency: str,
        gateway: PaymentGateway,
        payment_method_type: PaymentMethodType
    ) -> PaymentResult:
        """Process a successful payment."""
        self._transaction_counter += 1
        
        # Generate realistic transaction ID
        gateway_transaction_id = self._generate_transaction_id(gateway)
        
        # Create gateway response
        gateway_response = {
            "id": gateway_transaction_id,
            "amount": amount,
            "currency": currency,
            "status": "succeeded",
            "payment_method": payment_method_type.value.lower(),
            "created": int(datetime.utcnow().timestamp()),
            "gateway": gateway.value,
        }
        
        # Add gateway-specific fields
        if gateway == PaymentGateway.STRIPE_MOCK:
            gateway_response.update({
                "balance_transaction": f"txn_{uuid.uuid4().hex[:16]}",
                "receipt_url": f"https://pay.stripe.com/receipts/{uuid.uuid4().hex}",
            })
        elif gateway == PaymentGateway.PAYPAL_MOCK:
            gateway_response.update({
                "payer_id": f"PAYER{random.randint(100000, 999999)}",
                "transaction_fee": {"value": str(amount * 0.029 + 30), "currency": currency},
            })
        elif gateway == PaymentGateway.SQUARE_MOCK:
            gateway_response.update({
                "application_id": f"sq0idp-{uuid.uuid4().hex[:16]}",
                "location_id": f"LOC_{uuid.uuid4().hex[:8].upper()}",
            })
        
        return PaymentResult(
            success=True,
            status=PaymentStatus.COMPLETED,
            gateway_transaction_id=gateway_transaction_id,
            gateway=gateway,
            gateway_response=gateway_response
        )
    
    async def _process_failed_payment(
        self,
        payment_id: str,
        amount: int,
        currency: str,
        gateway: PaymentGateway,
        payment_method_type: PaymentMethodType
    ) -> PaymentResult:
        """Process a failed payment."""
        # Select failure reason based on distribution
        failure_reason = self._select_failure_reason()
        
        # Generate error details
        error_code, error_message, gateway_response = self._generate_error_details(
            failure_reason, gateway, amount, currency
        )
        
        return PaymentResult(
            success=False,
            status=PaymentStatus.FAILED,
            failure_reason=error_message,
            error_code=error_code,
            gateway=gateway,
            gateway_response=gateway_response
        )
    
    def _select_failure_reason(self) -> PaymentFailureReason:
        """Select failure reason based on configured distribution."""
        reasons = list(self.config.failure_distribution.keys())
        weights = list(self.config.failure_distribution.values())
        return random.choices(reasons, weights=weights)[0]
    
    def _generate_error_details(
        self,
        failure_reason: PaymentFailureReason,
        gateway: PaymentGateway,
        amount: int,
        currency: str
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Generate realistic error details for failed payments."""
        error_mappings = {
            PaymentFailureReason.INSUFFICIENT_FUNDS: {
                "code": "insufficient_funds",
                "message": "Your card has insufficient funds",
                "gateway_error": "insufficient_funds"
            },
            PaymentFailureReason.CARD_DECLINED: {
                "code": "card_declined",
                "message": "Your card was declined",
                "gateway_error": "generic_decline"
            },
            PaymentFailureReason.NETWORK_ERROR: {
                "code": "network_error",
                "message": "Network error occurred during processing",
                "gateway_error": "processing_error"
            },
            PaymentFailureReason.INVALID_PAYMENT_METHOD: {
                "code": "invalid_payment_method",
                "message": "Payment method is invalid or not supported",
                "gateway_error": "invalid_request_error"
            },
        }
        
        error_info = error_mappings[failure_reason]
        
        # Create gateway-specific response
        gateway_response = {
            "error": {
                "type": error_info["gateway_error"],
                "code": error_info["code"],
                "message": error_info["message"],
                "decline_code": error_info["code"] if "declined" in error_info["message"] else None,
            },
            "amount": amount,
            "currency": currency,
            "gateway": gateway.value,
            "created": int(datetime.utcnow().timestamp()),
        }
        
        # Remove None values
        gateway_response["error"] = {k: v for k, v in gateway_response["error"].items() if v is not None}
        
        return error_info["code"], error_info["message"], gateway_response
    
    def _generate_transaction_id(self, gateway: PaymentGateway) -> str:
        """Generate realistic transaction ID based on gateway."""
        base_id = uuid.uuid4().hex
        
        if gateway == PaymentGateway.STRIPE_MOCK:
            return f"ch_{base_id[:24]}"
        elif gateway == PaymentGateway.PAYPAL_MOCK:
            return f"PAY-{base_id[:17].upper()}"
        elif gateway == PaymentGateway.SQUARE_MOCK:
            return f"sq_{base_id[:20]}"
        else:
            return f"txn_{base_id[:16]}"
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            "total_transactions": self._transaction_counter,
            "success_rate": self.config.success_rate,
            "average_processing_time_ms": (
                self.config.processing_delay_min + self.config.processing_delay_max
            ) // 2,
            "failure_scenarios_enabled": self.config.failure_scenarios_enabled,
            "supported_gateways": [g.value for g in PaymentGateway],
        }


# Global processor instance
_processor_instance: Optional[MockPaymentProcessor] = None


def get_payment_processor() -> MockPaymentProcessor:
    """Get singleton payment processor instance."""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = MockPaymentProcessor()
    return _processor_instance


def reset_payment_processor():
    """Reset payment processor instance (for testing)."""
    global _processor_instance
    _processor_instance = None
