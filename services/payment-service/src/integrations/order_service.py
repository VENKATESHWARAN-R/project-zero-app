"""
Order Service Integration Client.

This module provides integration with the order service
for order validation, status updates, and order information retrieval.
"""

import os
from typing import Optional, Dict, Any
from uuid import UUID
import httpx
from datetime import datetime

from ..utils.logging import get_logger


logger = get_logger()


class OrderServiceError(Exception):
    """Base exception for order service errors."""
    pass


class OrderServiceUnavailableError(OrderServiceError):
    """Raised when order service is unavailable."""
    pass


class OrderNotFoundError(OrderServiceError):
    """Raised when order is not found."""
    pass


class OrderValidationError(OrderServiceError):
    """Raised when order validation fails."""
    pass


class OrderServiceClient:
    """
    Client for integrating with the order service.
    
    Provides methods for order validation, status updates,
    and order information retrieval.
    """
    
    def __init__(self, base_url: Optional[str] = None, timeout: float = 10.0):
        """
        Initialize order service client.
        
        Args:
            base_url: Base URL of the order service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv("ORDER_SERVICE_URL", "http://localhost:8008")
        self.timeout = timeout
        self._client = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
    
    async def get_order(self, order_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """
        Get order information by order ID.
        
        Args:
            order_id: Order ID to retrieve
            user_id: User ID for authorization
            
        Returns:
            Order information
            
        Raises:
            OrderNotFoundError: If order is not found
            OrderServiceUnavailableError: If order service is unavailable
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/orders/{order_id}",
                    headers={
                        "X-User-ID": str(user_id),
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    order_data = response.json()
                    logger.info(f"Retrieved order {order_id} for user {user_id}")
                    return order_data
                elif response.status_code == 404:
                    logger.warning(f"Order {order_id} not found")
                    raise OrderNotFoundError(f"Order {order_id} not found")
                elif response.status_code == 403:
                    logger.warning(f"User {user_id} not authorized for order {order_id}")
                    raise OrderNotFoundError(f"Order {order_id} not found or not accessible")
                else:
                    logger.error(f"Order service returned status {response.status_code}: {response.text}")
                    raise OrderServiceUnavailableError(f"Order service error: {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error("Order service request timed out")
            raise OrderServiceUnavailableError("Order service timeout")
        except httpx.ConnectError:
            logger.error("Failed to connect to order service")
            raise OrderServiceUnavailableError("Order service unavailable")
        except (OrderNotFoundError, OrderValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting order: {e}")
            raise OrderServiceUnavailableError(f"Order service error: {str(e)}")
    
    async def validate_order_for_payment(self, order_id: UUID, user_id: UUID, amount: int) -> Dict[str, Any]:
        """
        Validate that an order can be paid for.
        
        Args:
            order_id: Order ID to validate
            user_id: User ID for authorization
            amount: Payment amount in cents to validate
            
        Returns:
            Order validation result
            
        Raises:
            OrderValidationError: If order cannot be paid for
            OrderNotFoundError: If order is not found
            OrderServiceUnavailableError: If order service is unavailable
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/orders/{order_id}/validate-payment",
                    json={
                        "amount": amount,
                        "user_id": str(user_id)
                    },
                    headers={
                        "X-User-ID": str(user_id),
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    validation_result = response.json()
                    logger.info(f"Order {order_id} validated for payment: {validation_result}")
                    return validation_result
                elif response.status_code == 400:
                    error_data = response.json()
                    logger.warning(f"Order {order_id} validation failed: {error_data}")
                    raise OrderValidationError(error_data.get("error", "Order validation failed"))
                elif response.status_code == 404:
                    logger.warning(f"Order {order_id} not found for validation")
                    raise OrderNotFoundError(f"Order {order_id} not found")
                else:
                    logger.error(f"Order service returned status {response.status_code}: {response.text}")
                    raise OrderServiceUnavailableError(f"Order service error: {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error("Order service request timed out")
            raise OrderServiceUnavailableError("Order service timeout")
        except httpx.ConnectError:
            logger.error("Failed to connect to order service")
            raise OrderServiceUnavailableError("Order service unavailable")
        except (OrderNotFoundError, OrderValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error validating order: {e}")
            raise OrderServiceUnavailableError(f"Order service error: {str(e)}")
    
    async def update_order_payment_status(
        self,
        order_id: UUID,
        payment_id: UUID,
        status: str,
        amount: int,
        currency: str,
        gateway_transaction_id: Optional[str] = None,
        processed_at: Optional[datetime] = None
    ) -> bool:
        """
        Update order payment status after payment processing.
        
        Args:
            order_id: Order ID to update
            payment_id: Payment ID that was processed
            status: Payment status (COMPLETED, FAILED, etc.)
            amount: Payment amount in cents
            currency: Payment currency
            gateway_transaction_id: Gateway transaction ID (if successful)
            processed_at: Payment processing timestamp
            
        Returns:
            True if update was successful, False otherwise
            
        Raises:
            OrderServiceUnavailableError: If order service is unavailable
        """
        try:
            update_data = {
                "payment_id": str(payment_id),
                "payment_status": status,
                "amount": amount,
                "currency": currency
            }
            
            if gateway_transaction_id:
                update_data["gateway_transaction_id"] = gateway_transaction_id
            
            if processed_at:
                update_data["processed_at"] = processed_at.isoformat()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/orders/{order_id}/payment-status",
                    json=update_data,
                    headers={
                        "X-Service-Name": "payment-service",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code in [200, 204]:
                    logger.info(f"Updated order {order_id} payment status to {status}")
                    return True
                else:
                    logger.error(f"Failed to update order payment status: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.TimeoutException:
            logger.error("Order service request timed out")
            raise OrderServiceUnavailableError("Order service timeout")
        except httpx.ConnectError:
            logger.error("Failed to connect to order service")
            raise OrderServiceUnavailableError("Order service unavailable")
        except Exception as e:
            logger.error(f"Unexpected error updating order payment status: {e}")
            raise OrderServiceUnavailableError(f"Order service error: {str(e)}")
    
    async def notify_payment_completed(
        self,
        order_id: UUID,
        payment_id: UUID,
        amount: int,
        currency: str,
        gateway_transaction_id: Optional[str] = None,
        processed_at: Optional[datetime] = None
    ) -> bool:
        """
        Notify order service of successful payment completion.
        
        Args:
            order_id: Order ID that was paid for
            payment_id: Payment ID that was completed
            amount: Payment amount in cents
            currency: Payment currency
            gateway_transaction_id: Gateway transaction ID
            processed_at: Payment processing timestamp
            
        Returns:
            True if notification was successful, False otherwise
        """
        return await self.update_order_payment_status(
            order_id=order_id,
            payment_id=payment_id,
            status="COMPLETED",
            amount=amount,
            currency=currency,
            gateway_transaction_id=gateway_transaction_id,
            processed_at=processed_at
        )
    
    async def notify_payment_failed(
        self,
        order_id: UUID,
        payment_id: UUID,
        amount: int,
        currency: str,
        failure_reason: Optional[str] = None
    ) -> bool:
        """
        Notify order service of payment failure.
        
        Args:
            order_id: Order ID that payment failed for
            payment_id: Payment ID that failed
            amount: Payment amount in cents
            currency: Payment currency
            failure_reason: Reason for payment failure
            
        Returns:
            True if notification was successful, False otherwise
        """
        try:
            update_data = {
                "payment_id": str(payment_id),
                "payment_status": "FAILED",
                "amount": amount,
                "currency": currency
            }
            
            if failure_reason:
                update_data["failure_reason"] = failure_reason
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/orders/{order_id}/payment-status",
                    json=update_data,
                    headers={
                        "X-Service-Name": "payment-service",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code in [200, 204]:
                    logger.info(f"Notified order {order_id} of payment failure")
                    return True
                else:
                    logger.error(f"Failed to notify order of payment failure: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error notifying order service of payment failure: {e}")
            return False
    
    async def health_check(self) -> bool:
        """
        Check if order service is healthy and responding.
        
        Returns:
            True if order service is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False


# Global order service client instance
_order_client = None


def get_order_service_client() -> OrderServiceClient:
    """
    Get global order service client instance.
    
    Returns:
        OrderServiceClient instance
    """
    global _order_client
    if _order_client is None:
        _order_client = OrderServiceClient()
    return _order_client


async def validate_order_payment(order_id: UUID, user_id: UUID, amount: int) -> Dict[str, Any]:
    """
    Validate that an order can be paid for.
    
    Convenience function for order validation.
    
    Args:
        order_id: Order ID to validate
        user_id: User ID for authorization
        amount: Payment amount in cents
        
    Returns:
        Order validation result
        
    Raises:
        OrderValidationError: If order cannot be paid for
        OrderNotFoundError: If order is not found
        OrderServiceUnavailableError: If order service is unavailable
    """
    client = get_order_service_client()
    return await client.validate_order_for_payment(order_id, user_id, amount)


async def notify_order_payment_completed(
    order_id: UUID,
    payment_id: UUID,
    amount: int,
    currency: str,
    gateway_transaction_id: Optional[str] = None,
    processed_at: Optional[datetime] = None
) -> bool:
    """
    Notify order service of successful payment completion.
    
    Convenience function for payment completion notification.
    
    Args:
        order_id: Order ID that was paid for
        payment_id: Payment ID that was completed
        amount: Payment amount in cents
        currency: Payment currency
        gateway_transaction_id: Gateway transaction ID
        processed_at: Payment processing timestamp
        
    Returns:
        True if notification was successful, False otherwise
    """
    client = get_order_service_client()
    return await client.notify_payment_completed(
        order_id=order_id,
        payment_id=payment_id,
        amount=amount,
        currency=currency,
        gateway_transaction_id=gateway_transaction_id,
        processed_at=processed_at
    )


async def check_order_service_health() -> bool:
    """
    Check if order service is healthy.
    
    Convenience function for health checking.
    
    Returns:
        True if order service is healthy, False otherwise
    """
    client = get_order_service_client()
    return await client.health_check()


# Mock implementation for development/testing
class MockOrderServiceClient(OrderServiceClient):
    """
    Mock order service client for development and testing.
    
    Provides realistic responses without requiring actual order service.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mock_orders = {
            "456e7890-e89b-12d3-a456-426614174000": {
                "order_id": "456e7890-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "PENDING_PAYMENT",
                "total_amount": 2999,
                "currency": "USD",
                "items": [
                    {
                        "product_id": "prod_123",
                        "quantity": 1,
                        "price": 2999,
                        "name": "Test Product"
                    }
                ],
                "created_at": "2025-09-27T00:00:00Z"
            }
        }
    
    async def get_order(self, order_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """Mock order retrieval."""
        order_str = str(order_id)
        if order_str in self.mock_orders:
            order = self.mock_orders[order_str]
            if order["user_id"] == str(user_id):
                return order
            else:
                raise OrderNotFoundError(f"Order {order_id} not found or not accessible")
        else:
            raise OrderNotFoundError(f"Order {order_id} not found")
    
    async def validate_order_for_payment(self, order_id: UUID, user_id: UUID, amount: int) -> Dict[str, Any]:
        """Mock order validation."""
        order = await self.get_order(order_id, user_id)
        
        if order["status"] != "PENDING_PAYMENT":
            raise OrderValidationError(f"Order {order_id} is not pending payment")
        
        if order["total_amount"] != amount:
            raise OrderValidationError(f"Payment amount {amount} does not match order total {order['total_amount']}")
        
        return {
            "valid": True,
            "order_id": str(order_id),
            "total_amount": order["total_amount"],
            "currency": order["currency"],
            "status": order["status"]
        }
    
    async def update_order_payment_status(
        self,
        order_id: UUID,
        payment_id: UUID,
        status: str,
        amount: int,
        currency: str,
        gateway_transaction_id: Optional[str] = None,
        processed_at: Optional[datetime] = None
    ) -> bool:
        """Mock order status update."""
        order_str = str(order_id)
        if order_str in self.mock_orders:
            # Update mock order status
            if status == "COMPLETED":
                self.mock_orders[order_str]["status"] = "PAID"
                self.mock_orders[order_str]["payment_id"] = str(payment_id)
                if gateway_transaction_id:
                    self.mock_orders[order_str]["gateway_transaction_id"] = gateway_transaction_id
            elif status == "FAILED":
                self.mock_orders[order_str]["status"] = "PAYMENT_FAILED"
            
            return True
        else:
            return False
    
    async def health_check(self) -> bool:
        """Mock health check."""
        return True


def get_mock_order_service_client() -> MockOrderServiceClient:
    """
    Get mock order service client for development/testing.
    
    Returns:
        MockOrderServiceClient instance
    """
    return MockOrderServiceClient()
