"""
Cart service client.

Handles cart retrieval and clearing operations.
"""

from typing import Dict, List, Any, Optional
import httpx

from ..config import settings
from ..logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)


class CartServiceError(Exception):
    """Raised when cart service operations fail."""
    pass


class CartClient:
    """Client for cart service interactions."""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize CartClient.

        Args:
            base_url: Cart service base URL, defaults to config setting
        """
        self.base_url = (base_url or settings.cart_service_url).rstrip('/')
        self.timeout = httpx.Timeout(10.0)  # 10 second timeout
        logger.info("CartClient initialized", extra={
            "base_url": self.base_url
        })

    async def get_cart(self, user_id: int, auth_token: str) -> Dict[str, Any]:
        """
        Retrieve cart contents for a user.

        Args:
            user_id: User ID
            auth_token: JWT token for authentication

        Returns:
            Cart data with items

        Raises:
            CartServiceError: If cart retrieval fails
            httpx.RequestError: If cart service is unavailable
        """
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

        correlation_id = get_correlation_id()
        if correlation_id:
            headers["x-correlation-id"] = correlation_id

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/cart",
                    headers=headers
                )

                if response.status_code == 200:
                    cart_data = response.json()
                    logger.info("Cart retrieved successfully", extra={
                        "user_id": user_id,
                        "item_count": len(cart_data.get("items", [])),
                        "subtotal": cart_data.get("subtotal", 0)
                    })
                    return cart_data

                elif response.status_code == 404:
                    # Empty cart or user not found
                    logger.info("Cart not found or empty", extra={
                        "user_id": user_id
                    })
                    return {
                        "user_id": user_id,
                        "items": [],
                        "subtotal": 0.0
                    }

                else:
                    logger.error("Cart service error", extra={
                        "status_code": response.status_code,
                        "response": response.text[:200],
                        "user_id": user_id
                    })
                    raise CartServiceError(f"Failed to retrieve cart: {response.status_code}")

        except httpx.RequestError as e:
            logger.error("Failed to connect to cart service", extra={
                "error": str(e),
                "base_url": self.base_url,
                "user_id": user_id
            })
            raise

    async def clear_cart(self, user_id: int, auth_token: str) -> Dict[str, Any]:
        """
        Clear all items from user's cart after successful order creation.

        Args:
            user_id: User ID
            auth_token: JWT token for authentication

        Returns:
            Success confirmation

        Raises:
            CartServiceError: If cart clearing fails
            httpx.RequestError: If cart service is unavailable
        """
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

        correlation_id = get_correlation_id()
        if correlation_id:
            headers["x-correlation-id"] = correlation_id

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    f"{self.base_url}/cart",
                    headers=headers
                )

                if response.status_code in [200, 204]:
                    logger.info("Cart cleared successfully", extra={
                        "user_id": user_id
                    })
                    return {"success": True, "message": "Cart cleared"}

                elif response.status_code == 404:
                    # Cart already empty
                    logger.info("Cart already empty", extra={
                        "user_id": user_id
                    })
                    return {"success": True, "message": "Cart was already empty"}

                else:
                    logger.error("Cart clear error", extra={
                        "status_code": response.status_code,
                        "response": response.text[:200],
                        "user_id": user_id
                    })
                    raise CartServiceError(f"Failed to clear cart: {response.status_code}")

        except httpx.RequestError as e:
            logger.error("Failed to connect to cart service for clearing", extra={
                "error": str(e),
                "base_url": self.base_url,
                "user_id": user_id
            })
            raise

    async def validate_cart_items(self, cart_data: Dict[str, Any]) -> bool:
        """
        Validate that cart contains valid items.

        Args:
            cart_data: Cart data from get_cart()

        Returns:
            True if cart is valid for order creation

        Raises:
            CartServiceError: If cart validation fails
        """
        items = cart_data.get("items", [])

        if not items:
            raise CartServiceError("Cart is empty")

        # Validate each item
        for item in items:
            if not item.get("product_id"):
                raise CartServiceError("Cart contains invalid item - missing product ID")

            if not item.get("quantity") or item["quantity"] <= 0:
                raise CartServiceError("Cart contains invalid item - invalid quantity")

            product = item.get("product", {})
            if not product.get("name"):
                raise CartServiceError("Cart contains invalid item - missing product name")

            if not product.get("price") or product["price"] <= 0:
                raise CartServiceError("Cart contains invalid item - invalid product price")

        subtotal = cart_data.get("subtotal", 0)
        if subtotal <= 0:
            raise CartServiceError("Cart subtotal is invalid")

        logger.debug("Cart validation successful", extra={
            "item_count": len(items),
            "subtotal": subtotal
        })

        return True

    def extract_order_items_from_cart(self, cart_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract order item data from cart data.

        Args:
            cart_data: Cart data from get_cart()

        Returns:
            List of order item dictionaries
        """
        order_items = []

        for cart_item in cart_data.get("items", []):
            product = cart_item.get("product", {})

            order_item = {
                "product_id": cart_item["product_id"],
                "product_name": product.get("name", "Unknown Product"),
                "product_sku": product.get("sku"),
                "quantity": cart_item["quantity"],
                "unit_price": product.get("price", 0.0),
                "weight": product.get("weight", 0.0)
            }

            # Calculate total price
            order_item["total_price"] = order_item["quantity"] * order_item["unit_price"]

            order_items.append(order_item)

        logger.debug("Order items extracted from cart", extra={
            "item_count": len(order_items),
            "total_items": sum(item["quantity"] for item in order_items)
        })

        return order_items