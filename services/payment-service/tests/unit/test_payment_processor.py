"""
Unit tests for the Payment Processor service.

Tests the mock payment processing logic, configuration handling,
failure scenarios, and realistic simulation features.
"""

import asyncio
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.services.payment_processor import (
    MockPaymentProcessor,
    PaymentProcessorConfig,
    PaymentResult,
    PaymentGateway,
    PaymentFailureReason,
    get_payment_processor,
    reset_payment_processor
)
from src.models.payment import PaymentStatus
from src.models.payment_method import PaymentMethodType


class TestPaymentProcessorConfig:
    """Test payment processor configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = PaymentProcessorConfig()
        
        assert config.success_rate == 0.95
        assert config.processing_delay_min == 1000
        assert config.processing_delay_max == 3000
        assert config.failure_scenarios_enabled is True
        assert len(config.failure_distribution) == 4
        assert sum(config.failure_distribution.values()) == 1.0
        assert len(config.gateway_weights) == 3
    
    @patch.dict('os.environ', {
        'PAYMENT_SUCCESS_RATE': '0.8',
        'PAYMENT_PROCESSING_DELAY_MIN': '500',
        'PAYMENT_PROCESSING_DELAY_MAX': '2000',
        'PAYMENT_FAILURE_SCENARIOS': 'false'
    })
    def test_config_from_environment(self):
        """Test configuration loading from environment variables."""
        config = PaymentProcessorConfig()
        
        assert config.success_rate == 0.8
        assert config.processing_delay_min == 500
        assert config.processing_delay_max == 2000
        assert config.failure_scenarios_enabled is False
    
    def test_failure_distribution_sums_to_one(self):
        """Test that failure distribution percentages sum to 1.0."""
        config = PaymentProcessorConfig()
        total = sum(config.failure_distribution.values())
        assert abs(total - 1.0) < 0.001  # Allow for floating point precision
    
    def test_gateway_weights_configuration(self):
        """Test gateway weight configuration."""
        config = PaymentProcessorConfig()
        
        assert PaymentGateway.STRIPE_MOCK in config.gateway_weights
        assert PaymentGateway.PAYPAL_MOCK in config.gateway_weights
        assert PaymentGateway.SQUARE_MOCK in config.gateway_weights
        assert config.gateway_weights[PaymentGateway.STRIPE_MOCK] == 0.7


class TestPaymentResult:
    """Test payment result data structure."""
    
    def test_successful_payment_result(self):
        """Test successful payment result creation."""
        result = PaymentResult(
            success=True,
            status=PaymentStatus.COMPLETED,
            gateway_transaction_id="ch_test123",
            gateway=PaymentGateway.STRIPE_MOCK,
            processing_time_ms=1500
        )
        
        assert result.success is True
        assert result.status == PaymentStatus.COMPLETED
        assert result.gateway_transaction_id == "ch_test123"
        assert result.gateway == PaymentGateway.STRIPE_MOCK
        assert result.processing_time_ms == 1500
        assert result.failure_reason is None
        assert isinstance(result.processed_at, datetime)
    
    def test_failed_payment_result(self):
        """Test failed payment result creation."""
        result = PaymentResult(
            success=False,
            status=PaymentStatus.FAILED,
            failure_reason="Card declined",
            error_code="card_declined",
            gateway=PaymentGateway.STRIPE_MOCK
        )
        
        assert result.success is False
        assert result.status == PaymentStatus.FAILED
        assert result.failure_reason == "Card declined"
        assert result.error_code == "card_declined"
        assert result.gateway_transaction_id is None
    
    def test_result_to_dict(self):
        """Test payment result serialization to dictionary."""
        result = PaymentResult(
            success=True,
            status=PaymentStatus.COMPLETED,
            gateway_transaction_id="ch_test123",
            gateway=PaymentGateway.STRIPE_MOCK,
            processing_time_ms=1500,
            gateway_response={"id": "ch_test123", "status": "succeeded"}
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["success"] is True
        assert result_dict["status"] == "COMPLETED"
        assert result_dict["gateway_transaction_id"] == "ch_test123"
        assert result_dict["gateway"] == "stripe_mock"
        assert result_dict["processing_time_ms"] == 1500
        assert result_dict["gateway_response"]["id"] == "ch_test123"
        assert "processed_at" in result_dict


class TestMockPaymentProcessor:
    """Test mock payment processor functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = PaymentProcessorConfig()
        self.processor = MockPaymentProcessor(self.config)
    
    @pytest.mark.asyncio
    async def test_successful_payment_processing(self):
        """Test successful payment processing."""
        # Force success by setting success rate to 1.0
        self.config.success_rate = 1.0
        self.config.processing_delay_min = 10  # Reduce delay for testing
        self.config.processing_delay_max = 20
        
        result = await self.processor.process_payment(
            payment_id="test-payment-123",
            amount=5000,  # $50.00
            currency="USD",
            payment_method_type=PaymentMethodType.CREDIT_CARD,
            payment_method_details={"card_number": "4111111111111111"},
            order_id="order-123"
        )
        
        assert result.success is True
        assert result.status == PaymentStatus.COMPLETED
        assert result.gateway_transaction_id is not None
        assert result.gateway in [PaymentGateway.STRIPE_MOCK, PaymentGateway.SQUARE_MOCK]
        assert result.processing_time_ms > 0
        assert result.gateway_response is not None
    
    @pytest.mark.asyncio
    async def test_failed_payment_processing(self):
        """Test failed payment processing."""
        # Force failure by setting success rate to 0.0
        self.config.success_rate = 0.0
        self.config.processing_delay_min = 10
        self.config.processing_delay_max = 20
        
        result = await self.processor.process_payment(
            payment_id="test-payment-123",
            amount=5000,
            currency="USD",
            payment_method_type=PaymentMethodType.CREDIT_CARD,
            payment_method_details={"card_number": "4111111111111111"}
        )
        
        assert result.success is False
        assert result.status == PaymentStatus.FAILED
        assert result.failure_reason is not None
        assert result.error_code is not None
        assert result.gateway_transaction_id is None
        assert result.gateway_response is not None
    
    @pytest.mark.asyncio
    async def test_paypal_gateway_selection(self):
        """Test PayPal gateway selection for PayPal payments."""
        self.config.success_rate = 1.0
        self.config.processing_delay_min = 10
        self.config.processing_delay_max = 20
        
        result = await self.processor.process_payment(
            payment_id="test-payment-123",
            amount=5000,
            currency="USD",
            payment_method_type=PaymentMethodType.PAYPAL,
            payment_method_details={"email": "user@example.com"}
        )
        
        assert result.gateway == PaymentGateway.PAYPAL_MOCK
        assert result.gateway_transaction_id.startswith("PAY-")
    
    @pytest.mark.asyncio
    async def test_forced_failure_scenarios(self):
        """Test forced failure scenarios based on amount."""
        self.config.processing_delay_min = 10
        self.config.processing_delay_max = 20
        
        # Test insufficient funds (amount ending in 01)
        result = await self.processor.process_payment(
            payment_id="test-payment-123",
            amount=1501,  # Ends in 01
            currency="USD",
            payment_method_type=PaymentMethodType.CREDIT_CARD,
            payment_method_details={"card_number": "4111111111111111"}
        )
        
        assert result.success is False
        assert result.status == PaymentStatus.FAILED
        assert "Insufficient funds" in result.failure_reason
        assert result.error_code == "insufficient_funds"
    
    @pytest.mark.asyncio
    async def test_card_declined_scenario(self):
        """Test card declined scenario (amount ending in 02)."""
        self.config.processing_delay_min = 10
        self.config.processing_delay_max = 20
        
        result = await self.processor.process_payment(
            payment_id="test-payment-123",
            amount=1502,  # Ends in 02
            currency="USD",
            payment_method_type=PaymentMethodType.CREDIT_CARD,
            payment_method_details={"card_number": "4111111111111111"}
        )
        
        assert result.success is False
        assert result.status == PaymentStatus.FAILED
        assert "Card declined" in result.failure_reason
        assert result.error_code == "card_declined"
    
    @pytest.mark.asyncio
    async def test_network_error_scenario(self):
        """Test network error scenario (amount ending in 03)."""
        self.config.processing_delay_min = 10
        self.config.processing_delay_max = 20
        
        result = await self.processor.process_payment(
            payment_id="test-payment-123",
            amount=1503,  # Ends in 03
            currency="USD",
            payment_method_type=PaymentMethodType.CREDIT_CARD,
            payment_method_details={"card_number": "4111111111111111"}
        )
        
        assert result.success is False
        assert result.status == PaymentStatus.FAILED
        assert "Network error" in result.failure_reason
        assert result.error_code == "network_error"
    
    @pytest.mark.asyncio
    async def test_invalid_payment_method_scenario(self):
        """Test invalid payment method scenario (amount ending in 04)."""
        self.config.processing_delay_min = 10
        self.config.processing_delay_max = 20
        
        result = await self.processor.process_payment(
            payment_id="test-payment-123",
            amount=1504,  # Ends in 04
            currency="USD",
            payment_method_type=PaymentMethodType.CREDIT_CARD,
            payment_method_details={"card_number": "4111111111111111"}
        )
        
        assert result.success is False
        assert result.status == PaymentStatus.FAILED
        assert "Invalid payment method" in result.failure_reason
        assert result.error_code == "invalid_payment_method"
    
    @pytest.mark.asyncio
    async def test_processing_delay(self):
        """Test that processing delay is applied."""
        self.config.processing_delay_min = 100  # 100ms
        self.config.processing_delay_max = 200  # 200ms
        
        start_time = datetime.utcnow()
        
        result = await self.processor.process_payment(
            payment_id="test-payment-123",
            amount=5000,
            currency="USD",
            payment_method_type=PaymentMethodType.CREDIT_CARD,
            payment_method_details={"card_number": "4111111111111111"}
        )
        
        end_time = datetime.utcnow()
        actual_delay = (end_time - start_time).total_seconds() * 1000
        
        # Should have at least the minimum delay
        assert actual_delay >= 100
        assert result.processing_time_ms >= 100
    
    def test_transaction_id_generation(self):
        """Test transaction ID generation for different gateways."""
        # Test Stripe transaction ID
        stripe_id = self.processor._generate_transaction_id(PaymentGateway.STRIPE_MOCK)
        assert stripe_id.startswith("ch_")
        assert len(stripe_id) == 27  # "ch_" + 24 characters
        
        # Test PayPal transaction ID
        paypal_id = self.processor._generate_transaction_id(PaymentGateway.PAYPAL_MOCK)
        assert paypal_id.startswith("PAY-")
        assert len(paypal_id) == 21  # "PAY-" + 17 characters
        
        # Test Square transaction ID
        square_id = self.processor._generate_transaction_id(PaymentGateway.SQUARE_MOCK)
        assert square_id.startswith("sq_")
        assert len(square_id) == 23  # "sq_" + 20 characters
    
    def test_gateway_selection_for_cards(self):
        """Test gateway selection logic for card payments."""
        # Test multiple selections to verify randomness and weights
        gateways = []
        for _ in range(100):
            gateway = self.processor._select_gateway(PaymentMethodType.CREDIT_CARD)
            gateways.append(gateway)
        
        # Should not select PayPal for card payments
        assert PaymentGateway.PAYPAL_MOCK not in gateways
        
        # Should include Stripe and Square
        assert PaymentGateway.STRIPE_MOCK in gateways
        assert PaymentGateway.SQUARE_MOCK in gateways
    
    def test_failure_reason_selection(self):
        """Test failure reason selection based on distribution."""
        reasons = []
        for _ in range(100):
            reason = self.processor._select_failure_reason()
            reasons.append(reason)
        
        # Should include all configured failure reasons
        unique_reasons = set(reasons)
        expected_reasons = set(self.config.failure_distribution.keys())
        assert unique_reasons.issubset(expected_reasons)
    
    def test_get_processing_stats(self):
        """Test processing statistics retrieval."""
        stats = self.processor.get_processing_stats()
        
        assert "total_transactions" in stats
        assert "success_rate" in stats
        assert "average_processing_time_ms" in stats
        assert "failure_scenarios_enabled" in stats
        assert "supported_gateways" in stats
        
        assert stats["success_rate"] == self.config.success_rate
        assert stats["failure_scenarios_enabled"] == self.config.failure_scenarios_enabled
        assert len(stats["supported_gateways"]) == 3
    
    @pytest.mark.asyncio
    async def test_gateway_specific_response_fields(self):
        """Test that gateway-specific fields are included in responses."""
        self.config.success_rate = 1.0
        self.config.processing_delay_min = 10
        self.config.processing_delay_max = 20
        
        # Test Stripe response
        with patch.object(self.processor, '_select_gateway', return_value=PaymentGateway.STRIPE_MOCK):
            result = await self.processor.process_payment(
                payment_id="test-payment-123",
                amount=5000,
                currency="USD",
                payment_method_type=PaymentMethodType.CREDIT_CARD,
                payment_method_details={"card_number": "4111111111111111"}
            )
            
            assert "balance_transaction" in result.gateway_response
            assert "receipt_url" in result.gateway_response
            assert result.gateway_response["gateway"] == "stripe_mock"
        
        # Test PayPal response
        result = await self.processor.process_payment(
            payment_id="test-payment-123",
            amount=5000,
            currency="USD",
            payment_method_type=PaymentMethodType.PAYPAL,
            payment_method_details={"email": "user@example.com"}
        )
        
        assert "payer_id" in result.gateway_response
        assert "transaction_fee" in result.gateway_response
        assert result.gateway_response["gateway"] == "paypal_mock"
    
    @pytest.mark.asyncio
    async def test_disabled_failure_scenarios(self):
        """Test behavior when failure scenarios are disabled."""
        self.config.failure_scenarios_enabled = False
        self.config.success_rate = 1.0
        self.config.processing_delay_min = 10
        self.config.processing_delay_max = 20
        
        # Test amount that would normally trigger failure
        result = await self.processor.process_payment(
            payment_id="test-payment-123",
            amount=1501,  # Would normally trigger insufficient funds
            currency="USD",
            payment_method_type=PaymentMethodType.CREDIT_CARD,
            payment_method_details={"card_number": "4111111111111111"}
        )
        
        # Should succeed because failure scenarios are disabled
        assert result.success is True
        assert result.status == PaymentStatus.COMPLETED


class TestPaymentProcessorSingleton:
    """Test payment processor singleton functionality."""
    
    def setup_method(self):
        """Reset singleton before each test."""
        reset_payment_processor()
    
    def test_singleton_instance(self):
        """Test that get_payment_processor returns singleton instance."""
        processor1 = get_payment_processor()
        processor2 = get_payment_processor()
        
        assert processor1 is processor2
        assert isinstance(processor1, MockPaymentProcessor)
    
    def test_reset_processor(self):
        """Test processor reset functionality."""
        processor1 = get_payment_processor()
        reset_payment_processor()
        processor2 = get_payment_processor()
        
        assert processor1 is not processor2
        assert isinstance(processor2, MockPaymentProcessor)


class TestPaymentProcessorIntegration:
    """Integration tests for payment processor with realistic scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = MockPaymentProcessor()
    
    @pytest.mark.asyncio
    async def test_concurrent_payment_processing(self):
        """Test concurrent payment processing."""
        # Create multiple payment tasks
        tasks = []
        for i in range(10):
            task = self.processor.process_payment(
                payment_id=f"test-payment-{i}",
                amount=5000 + i,
                currency="USD",
                payment_method_type=PaymentMethodType.CREDIT_CARD,
                payment_method_details={"card_number": "4111111111111111"}
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all payments were processed
        assert len(results) == 10
        for result in results:
            assert isinstance(result, PaymentResult)
            assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_different_payment_methods(self):
        """Test processing different payment method types."""
        payment_methods = [
            (PaymentMethodType.CREDIT_CARD, {"card_number": "4111111111111111"}),
            (PaymentMethodType.DEBIT_CARD, {"card_number": "4000056655665556"}),
            (PaymentMethodType.PAYPAL, {"email": "user@example.com"})
        ]
        
        for method_type, details in payment_methods:
            result = await self.processor.process_payment(
                payment_id=f"test-payment-{method_type.value}",
                amount=5000,
                currency="USD",
                payment_method_type=method_type,
                payment_method_details=details
            )
            
            assert isinstance(result, PaymentResult)
            if method_type == PaymentMethodType.PAYPAL:
                assert result.gateway == PaymentGateway.PAYPAL_MOCK
            else:
                assert result.gateway in [PaymentGateway.STRIPE_MOCK, PaymentGateway.SQUARE_MOCK]
    
    @pytest.mark.asyncio
    async def test_realistic_success_failure_distribution(self):
        """Test that success/failure distribution matches configuration."""
        config = PaymentProcessorConfig()
        config.success_rate = 0.8  # 80% success rate
        config.processing_delay_min = 1
        config.processing_delay_max = 5
        processor = MockPaymentProcessor(config)
        
        results = []
        for i in range(100):
            # Use amounts that don't trigger forced scenarios
            result = await processor.process_payment(
                payment_id=f"test-payment-{i}",
                amount=5000 + (i % 10),  # Avoid forced failure amounts
                currency="USD",
                payment_method_type=PaymentMethodType.CREDIT_CARD,
                payment_method_details={"card_number": "4111111111111111"}
            )
            results.append(result)
        
        successful_payments = sum(1 for r in results if r.success)
        success_rate = successful_payments / len(results)
        
        # Allow for some variance due to randomness (±15%)
        assert 0.65 <= success_rate <= 0.95
