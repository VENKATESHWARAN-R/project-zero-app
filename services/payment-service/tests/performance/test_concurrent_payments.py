"""
Performance tests for concurrent payment processing.

Tests the payment service's ability to handle multiple concurrent
payment requests while maintaining performance and data consistency.
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
import pytest
from unittest.mock import MagicMock, patch

from src.services.payment_processor import MockPaymentProcessor, PaymentProcessorConfig
from src.services.payment_validator import PaymentValidator
from src.services.webhook_simulator import WebhookSimulator, WebhookConfig
from src.models.payment_method import PaymentMethodType


class PerformanceMetrics:
    """Container for performance test metrics."""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.success_count: int = 0
        self.failure_count: int = 0
        self.error_count: int = 0
        self.start_time: float = 0
        self.end_time: float = 0
    
    def add_result(self, response_time: float, success: bool, error: bool = False):
        """Add a test result to metrics."""
        self.response_times.append(response_time)
        if error:
            self.error_count += 1
        elif success:
            self.success_count += 1
        else:
            self.failure_count += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.response_times:
            return {}
        
        total_duration = self.end_time - self.start_time
        total_requests = len(self.response_times)
        
        return {
            "total_requests": total_requests,
            "total_duration_seconds": total_duration,
            "requests_per_second": total_requests / total_duration if total_duration > 0 else 0,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / total_requests if total_requests > 0 else 0,
            "avg_response_time_ms": statistics.mean(self.response_times),
            "median_response_time_ms": statistics.median(self.response_times),
            "min_response_time_ms": min(self.response_times),
            "max_response_time_ms": max(self.response_times),
            "p95_response_time_ms": self._percentile(self.response_times, 95),
            "p99_response_time_ms": self._percentile(self.response_times, 99),
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of response times."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]


class TestConcurrentPaymentProcessing:
    """Test concurrent payment processing performance."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Configure for performance testing
        self.config = PaymentProcessorConfig()
        self.config.processing_delay_min = 10  # Reduced for testing
        self.config.processing_delay_max = 50
        self.config.success_rate = 0.95
        
        self.processor = MockPaymentProcessor(self.config)
        self.validator = PaymentValidator()
    
    @pytest.mark.asyncio
    async def test_concurrent_payment_processing_load(self):
        """Test payment processing under concurrent load."""
        concurrent_requests = 50
        metrics = PerformanceMetrics()
        
        async def process_single_payment(payment_id: int) -> Dict[str, Any]:
            """Process a single payment and measure performance."""
            start_time = time.time()
            
            try:
                result = await self.processor.process_payment(
                    payment_id=f"perf-test-{payment_id}",
                    amount=5000 + (payment_id % 100),  # Vary amounts
                    currency="USD",
                    payment_method_type=PaymentMethodType.CREDIT_CARD,
                    payment_method_details={"card_number": "4111111111111111"}
                )
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to ms
                
                return {
                    "response_time": response_time,
                    "success": result.success,
                    "error": False,
                    "result": result
                }
            
            except Exception as e:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                return {
                    "response_time": response_time,
                    "success": False,
                    "error": True,
                    "exception": str(e)
                }
        
        # Execute concurrent payments
        metrics.start_time = time.time()
        
        tasks = [
            process_single_payment(i)
            for i in range(concurrent_requests)
        ]
        
        results = await asyncio.gather(*tasks)
        
        metrics.end_time = time.time()
        
        # Collect metrics
        for result in results:
            metrics.add_result(
                response_time=result["response_time"],
                success=result["success"],
                error=result["error"]
            )
        
        # Analyze performance
        stats = metrics.get_statistics()
        
        # Performance assertions
        assert stats["total_requests"] == concurrent_requests
        assert stats["error_count"] == 0, f"Unexpected errors: {stats['error_count']}"
        assert stats["avg_response_time_ms"] < 500, f"Average response time too high: {stats['avg_response_time_ms']}ms"
        assert stats["p95_response_time_ms"] < 1000, f"95th percentile too high: {stats['p95_response_time_ms']}ms"
        assert stats["requests_per_second"] > 10, f"Throughput too low: {stats['requests_per_second']} req/s"
        
        # Print performance summary
        print(f"\nConcurrent Payment Processing Performance:")
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  Duration: {stats['total_duration_seconds']:.2f}s")
        print(f"  Throughput: {stats['requests_per_second']:.2f} req/s")
        print(f"  Success Rate: {stats['success_rate']:.2%}")
        print(f"  Avg Response Time: {stats['avg_response_time_ms']:.2f}ms")
        print(f"  95th Percentile: {stats['p95_response_time_ms']:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_payment_validation_performance(self):
        """Test payment validation performance under load."""
        validation_requests = 1000
        metrics = PerformanceMetrics()
        
        async def validate_single_payment(request_id: int) -> Dict[str, Any]:
            """Validate a single payment request and measure performance."""
            start_time = time.time()
            
            try:
                result = self.validator.validate_payment_request(
                    amount=5000 + (request_id % 1000),
                    currency="USD",
                    order_id=f"550e8400-e29b-41d4-a716-44665544{request_id:04d}",
                    payment_method_id=f"550e8400-e29b-41d4-a716-44665544{(request_id+1):04d}",
                    user_id=f"550e8400-e29b-41d4-a716-44665544{(request_id+2):04d}",
                    description=f"Performance test payment {request_id}"
                )
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                return {
                    "response_time": response_time,
                    "success": result.is_valid,
                    "error": False,
                    "result": result
                }
            
            except Exception as e:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                return {
                    "response_time": response_time,
                    "success": False,
                    "error": True,
                    "exception": str(e)
                }
        
        # Execute validation requests
        metrics.start_time = time.time()
        
        # Process in batches to avoid overwhelming the system
        batch_size = 100
        all_results = []
        
        for i in range(0, validation_requests, batch_size):
            batch_end = min(i + batch_size, validation_requests)
            batch_tasks = [
                validate_single_payment(j)
                for j in range(i, batch_end)
            ]
            
            batch_results = await asyncio.gather(*batch_tasks)
            all_results.extend(batch_results)
        
        metrics.end_time = time.time()
        
        # Collect metrics
        for result in all_results:
            metrics.add_result(
                response_time=result["response_time"],
                success=result["success"],
                error=result["error"]
            )
        
        # Analyze performance
        stats = metrics.get_statistics()
        
        # Performance assertions
        assert stats["total_requests"] == validation_requests
        assert stats["error_count"] == 0, f"Unexpected errors: {stats['error_count']}"
        assert stats["avg_response_time_ms"] < 10, f"Validation too slow: {stats['avg_response_time_ms']}ms"
        assert stats["requests_per_second"] > 100, f"Validation throughput too low: {stats['requests_per_second']} req/s"
        
        # Print performance summary
        print(f"\nPayment Validation Performance:")
        print(f"  Total Validations: {stats['total_requests']}")
        print(f"  Duration: {stats['total_duration_seconds']:.2f}s")
        print(f"  Throughput: {stats['requests_per_second']:.2f} validations/s")
        print(f"  Avg Response Time: {stats['avg_response_time_ms']:.3f}ms")
    
    @pytest.mark.asyncio
    async def test_mixed_payment_method_performance(self):
        """Test performance with mixed payment method types."""
        requests_per_method = 20
        payment_methods = [
            (PaymentMethodType.CREDIT_CARD, {"card_number": "4111111111111111"}),
            (PaymentMethodType.DEBIT_CARD, {"card_number": "4000056655665556"}),
            (PaymentMethodType.PAYPAL, {"email": "user@example.com"})
        ]
        
        metrics = PerformanceMetrics()
        
        async def process_payment_by_method(method_type, details, request_id):
            """Process payment with specific method type."""
            start_time = time.time()
            
            try:
                result = await self.processor.process_payment(
                    payment_id=f"mixed-test-{method_type.value}-{request_id}",
                    amount=5000 + request_id,
                    currency="USD",
                    payment_method_type=method_type,
                    payment_method_details=details
                )
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                return {
                    "response_time": response_time,
                    "success": result.success,
                    "error": False,
                    "method_type": method_type.value,
                    "result": result
                }
            
            except Exception as e:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                return {
                    "response_time": response_time,
                    "success": False,
                    "error": True,
                    "method_type": method_type.value,
                    "exception": str(e)
                }
        
        # Create tasks for all payment methods
        tasks = []
        for method_type, details in payment_methods:
            for i in range(requests_per_method):
                tasks.append(process_payment_by_method(method_type, details, i))
        
        # Execute all payments concurrently
        metrics.start_time = time.time()
        results = await asyncio.gather(*tasks)
        metrics.end_time = time.time()
        
        # Collect metrics by payment method
        method_stats = {}
        for result in results:
            method_type = result["method_type"]
            if method_type not in method_stats:
                method_stats[method_type] = PerformanceMetrics()
            
            method_stats[method_type].add_result(
                response_time=result["response_time"],
                success=result["success"],
                error=result["error"]
            )
            
            metrics.add_result(
                response_time=result["response_time"],
                success=result["success"],
                error=result["error"]
            )
        
        # Analyze overall performance
        overall_stats = metrics.get_statistics()
        
        # Performance assertions
        assert overall_stats["error_count"] == 0
        assert overall_stats["avg_response_time_ms"] < 500
        
        # Print performance by method
        print(f"\nMixed Payment Method Performance:")
        print(f"  Overall Avg Response Time: {overall_stats['avg_response_time_ms']:.2f}ms")
        
        for method_type, method_metrics in method_stats.items():
            method_metrics.start_time = metrics.start_time
            method_metrics.end_time = metrics.end_time
            stats = method_metrics.get_statistics()
            print(f"  {method_type}:")
            print(f"    Requests: {stats['total_requests']}")
            print(f"    Avg Response Time: {stats['avg_response_time_ms']:.2f}ms")
            print(f"    Success Rate: {stats['success_rate']:.2%}")


class TestWebhookPerformance:
    """Test webhook delivery performance."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = WebhookConfig()
        self.config.delivery_delay_min = 1
        self.config.delivery_delay_max = 10
        self.config.success_rate = 0.95
        self.simulator = WebhookSimulator(self.config)
    
    @pytest.mark.asyncio
    async def test_concurrent_webhook_delivery_performance(self):
        """Test concurrent webhook delivery performance."""
        webhook_count = 30
        metrics = PerformanceMetrics()
        
        # Create mock webhook events
        webhook_events = []
        for i in range(webhook_count):
            webhook_event = MagicMock()
            webhook_event.id = f"webhook-perf-{i}"
            webhook_event.endpoint_url = f"http://localhost:808{i % 10}/webhook"
            webhook_event.payload = {"test": f"data-{i}"}
            webhook_event.created_at = time.time()
            webhook_events.append(webhook_event)
        
        async def deliver_single_webhook(webhook_event):
            """Deliver single webhook and measure performance."""
            start_time = time.time()
            
            try:
                with patch('httpx.AsyncClient.post') as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.text = "OK"
                    mock_post.return_value = mock_response
                    
                    result = await self.simulator.deliver_webhook(webhook_event)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                return {
                    "response_time": response_time,
                    "success": result.success,
                    "error": False,
                    "result": result
                }
            
            except Exception as e:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                return {
                    "response_time": response_time,
                    "success": False,
                    "error": True,
                    "exception": str(e)
                }
        
        # Execute concurrent webhook deliveries
        metrics.start_time = time.time()
        
        tasks = [
            deliver_single_webhook(webhook_event)
            for webhook_event in webhook_events
        ]
        
        results = await asyncio.gather(*tasks)
        
        metrics.end_time = time.time()
        
        # Collect metrics
        for result in results:
            metrics.add_result(
                response_time=result["response_time"],
                success=result["success"],
                error=result["error"]
            )
        
        # Analyze performance
        stats = metrics.get_statistics()
        
        # Performance assertions
        assert stats["total_requests"] == webhook_count
        assert stats["error_count"] == 0
        assert stats["avg_response_time_ms"] < 1000  # Including simulated delays
        
        # Print performance summary
        print(f"\nWebhook Delivery Performance:")
        print(f"  Total Webhooks: {stats['total_requests']}")
        print(f"  Duration: {stats['total_duration_seconds']:.2f}s")
        print(f"  Throughput: {stats['requests_per_second']:.2f} webhooks/s")
        print(f"  Success Rate: {stats['success_rate']:.2%}")
        print(f"  Avg Response Time: {stats['avg_response_time_ms']:.2f}ms")


class TestMemoryUsagePerformance:
    """Test memory usage under load."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = PaymentProcessorConfig()
        self.config.processing_delay_min = 1
        self.config.processing_delay_max = 5
        self.processor = MockPaymentProcessor(self.config)
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """Test memory usage doesn't grow excessively under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process many payments
        payment_count = 200
        batch_size = 50
        
        for batch in range(0, payment_count, batch_size):
            tasks = []
            for i in range(batch, min(batch + batch_size, payment_count)):
                task = self.processor.process_payment(
                    payment_id=f"memory-test-{i}",
                    amount=5000 + i,
                    currency="USD",
                    payment_method_type=PaymentMethodType.CREDIT_CARD,
                    payment_method_details={"card_number": "4111111111111111"}
                )
                tasks.append(task)
            
            # Process batch
            await asyncio.gather(*tasks)
            
            # Check memory usage
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_growth = current_memory - initial_memory
            
            # Memory shouldn't grow excessively (allow 50MB growth)
            assert memory_growth < 50, f"Memory usage grew too much: {memory_growth:.2f}MB"
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_growth = final_memory - initial_memory
        
        print(f"\nMemory Usage Test:")
        print(f"  Initial Memory: {initial_memory:.2f}MB")
        print(f"  Final Memory: {final_memory:.2f}MB")
        print(f"  Total Growth: {total_growth:.2f}MB")
        print(f"  Payments Processed: {payment_count}")
        
        # Final assertion
        assert total_growth < 100, f"Total memory growth too high: {total_growth:.2f}MB"
