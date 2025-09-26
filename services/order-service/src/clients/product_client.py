"""
Product catalog service client.

Handles product details retrieval and inventory validation.
"""

from typing import Dict, List, Any, Optional
import httpx

from ..config import settings
from ..logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)


class ProductServiceError(Exception):
    """Raised when product service operations fail."""
    pass


class ProductNotFoundError(ProductServiceError):
    """Raised when product is not found."""
    pass


class ProductUnavailableError(ProductServiceError):
    """Raised when product is unavailable."""
    pass


class ProductClient:
    """Client for product catalog service interactions."""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize ProductClient.

        Args:
            base_url: Product service base URL, defaults to config setting
        """
        self.base_url = (base_url or settings.product_service_url).rstrip('/')
        self.timeout = httpx.Timeout(10.0)  # 10 second timeout
        logger.info("ProductClient initialized", extra={
            "base_url": self.base_url
        })

    async def get_product_details(self, product_id: int) -> Dict[str, Any]:
        """
        Get detailed product information.

        Args:
            product_id: Product ID to retrieve

        Returns:
            Product details dictionary

        Raises:
            ProductNotFoundError: If product doesn't exist
            ProductServiceError: If product service fails
            httpx.RequestError: If service is unavailable
        """
        headers = {"Content-Type": "application/json"}

        correlation_id = get_correlation_id()
        if correlation_id:
            headers["x-correlation-id"] = correlation_id

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/products/{product_id}",
                    headers=headers
                )

                if response.status_code == 200:
                    product_data = response.json()
                    logger.debug("Product retrieved successfully", extra={
                        "product_id": product_id,
                        "product_name": product_data.get("name"),
                        "available": product_data.get("available", False)
                    })
                    return product_data

                elif response.status_code == 404:
                    logger.warning("Product not found", extra={
                        "product_id": product_id
                    })
                    raise ProductNotFoundError(f"Product {product_id} not found")

                else:
                    logger.error("Product service error", extra={
                        "status_code": response.status_code,
                        "response": response.text[:200],
                        "product_id": product_id
                    })
                    raise ProductServiceError(f"Failed to retrieve product: {response.status_code}")

        except httpx.RequestError as e:
            logger.error("Failed to connect to product service", extra={
                "error": str(e),
                "base_url": self.base_url,
                "product_id": product_id
            })
            raise

    async def validate_product_availability(self, product_id: int, quantity: int) -> Dict[str, Any]:
        """
        Validate product availability for the requested quantity.

        Args:
            product_id: Product ID to check
            quantity: Requested quantity

        Returns:
            Product data with availability confirmation

        Raises:
            ProductNotFoundError: If product doesn't exist
            ProductUnavailableError: If product is unavailable or insufficient stock
            ProductServiceError: If validation fails
        """
        product_data = await self.get_product_details(product_id)

        # Check basic availability
        if not product_data.get("available", False):
            logger.warning("Product unavailable", extra={
                "product_id": product_id,
                "product_name": product_data.get("name")
            })
            raise ProductUnavailableError(f"Product {product_id} is not available")

        # Check stock level if provided
        stock_level = product_data.get("stock_level")
        if stock_level is not None and stock_level < quantity:
            logger.warning("Insufficient stock", extra={
                "product_id": product_id,
                "requested_quantity": quantity,
                "available_stock": stock_level
            })
            raise ProductUnavailableError(
                f"Insufficient stock for product {product_id}. "
                f"Requested: {quantity}, Available: {stock_level}"
            )

        logger.info("Product availability validated", extra={
            "product_id": product_id,
            "quantity": quantity,
            "stock_level": stock_level
        })

        return product_data

    async def get_multiple_products(self, product_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Get details for multiple products.

        Args:
            product_ids: List of product IDs

        Returns:
            Dictionary mapping product_id to product data

        Raises:
            ProductServiceError: If batch retrieval fails
        """
        if not product_ids:
            return {}

        headers = {"Content-Type": "application/json"}

        correlation_id = get_correlation_id()
        if correlation_id:
            headers["x-correlation-id"] = correlation_id

        # Use batch endpoint if available, otherwise fetch individually
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Try batch endpoint first
                batch_params = {"ids": ",".join(map(str, product_ids))}
                response = await client.get(
                    f"{self.base_url}/products/batch",
                    params=batch_params,
                    headers=headers
                )

                if response.status_code == 200:
                    batch_data = response.json()
                    logger.info("Batch product retrieval successful", extra={
                        "product_count": len(batch_data.get("products", {}))
                    })
                    return batch_data.get("products", {})

        except httpx.RequestError:
            logger.warning("Batch endpoint unavailable, falling back to individual requests")

        # Fallback to individual requests
        products = {}
        for product_id in product_ids:
            try:
                product_data = await self.get_product_details(product_id)
                products[product_id] = product_data
            except ProductNotFoundError:
                logger.warning("Product not found during batch fetch", extra={
                    "product_id": product_id
                })
                # Continue with other products, don't include missing ones

        logger.info("Individual product retrieval completed", extra={
            "requested_count": len(product_ids),
            "retrieved_count": len(products)
        })

        return products

    async def validate_order_items(self, order_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate all items for an order.

        Args:
            order_items: List of order item dictionaries

        Returns:
            Updated order items with validated product data

        Raises:
            ProductServiceError: If validation fails for any item
        """
        validated_items = []

        for item in order_items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 0)

            if not product_id or quantity <= 0:
                raise ProductServiceError("Invalid order item data")

            # Validate product availability
            product_data = await self.validate_product_availability(product_id, quantity)

            # Update item with current product data
            validated_item = item.copy()
            validated_item.update({
                "product_name": product_data.get("name", item.get("product_name")),
                "product_sku": product_data.get("sku", item.get("product_sku")),
                "unit_price": product_data.get("price", item.get("unit_price", 0.0)),
                "weight": product_data.get("weight", item.get("weight", 0.0))
            })

            # Recalculate total price with current price
            validated_item["total_price"] = quantity * validated_item["unit_price"]

            validated_items.append(validated_item)

        logger.info("Order items validation completed", extra={
            "item_count": len(validated_items)
        })

        return validated_items