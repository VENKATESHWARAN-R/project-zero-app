"""
Integration test for complete order creation flow.

This test MUST FAIL until the full workflow is implemented.
Tests the complete order lifecycle from cart to order creation.
"""

import pytest
from unittest.mock import patch, Mock
from httpx import AsyncClient
from decimal import Decimal


class TestOrderCreationFlow:
    """Integration test for complete order creation workflow."""

    @pytest.mark.asyncio
    async def test_complete_order_creation_workflow(
        self,
        async_test_client: AsyncClient,
        sample_order_data,
        mock_jwt_token,
        mock_cart_response
    ):
        """
        Test the complete order creation workflow:
        1. User has items in cart
        2. User provides shipping address
        3. System calculates totals (tax + shipping)
        4. Order is created
        5. Cart is cleared
        6. Order can be retrieved
        """
        # Mock all external service dependencies
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth, \
             patch('src.clients.cart_client.CartClient.get_cart') as mock_get_cart, \
             patch('src.clients.cart_client.CartClient.clear_cart') as mock_clear_cart, \
             patch('src.clients.product_client.ProductClient.get_product_details') as mock_product, \
             patch('src.services.tax_service.TaxService.calculate_tax') as mock_tax, \
             patch('src.services.shipping_service.ShippingService.calculate_shipping_cost') as mock_shipping:

            # Setup all mocks
            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}
            mock_get_cart.return_value = mock_cart_response
            mock_clear_cart.return_value = {"success": True}

            # Mock product details for each cart item
            def mock_product_side_effect(product_id):
                products = {
                    2: {"id": 2, "name": "Test Product 1", "sku": "TEST-001", "available": True, "price": 29.99, "weight": 0.5},
                    3: {"id": 3, "name": "Test Product 2", "sku": "TEST-002", "available": True, "price": 29.99, "weight": 1.2}
                }
                return products.get(product_id, {"available": False})

            mock_product.side_effect = mock_product_side_effect
            mock_tax.return_value = 7.65  # 8.5% of 89.97
            mock_shipping.return_value = 8.99

            # Step 1: Create order
            create_response = await async_test_client.post(
                "/orders",
                json=sample_order_data,
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            # This SHOULD FAIL until complete implementation exists
            assert create_response.status_code == 201

            order_data = create_response.json()
            order_id = order_data["id"]

            # Verify order creation response
            assert order_data["user_id"] == 42
            assert order_data["status"] == "PENDING"
            assert order_data["subtotal"] == 89.97
            assert order_data["tax_amount"] == 7.65
            assert order_data["shipping_cost"] == 8.99
            assert order_data["total"] == 106.61
            assert order_data["currency"] == "USD"
            assert "order_number" in order_data
            assert "created_at" in order_data

            # Step 2: Verify cart was cleared
            mock_clear_cart.assert_called_once_with(42)

            # Step 3: Verify order can be retrieved with full details
            detail_response = await async_test_client.get(
                f"/orders/{order_id}",
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert detail_response.status_code == 200

            detail_data = detail_response.json()
            assert detail_data["id"] == order_id
            assert len(detail_data["items"]) == 2

            # Verify order items
            items = detail_data["items"]
            assert items[0]["product_name"] == "Test Product 1"
            assert items[0]["quantity"] == 2
            assert items[0]["unit_price"] == 29.99
            assert items[0]["total_price"] == 59.98

            assert items[1]["product_name"] == "Test Product 2"
            assert items[1]["quantity"] == 1
            assert items[1]["unit_price"] == 29.99
            assert items[1]["total_price"] == 29.99

            # Verify shipping address
            shipping = detail_data["shipping_address"]
            assert shipping["recipient_name"] == "John Doe"
            assert shipping["address_line_1"] == "123 Main Street"
            assert shipping["city"] == "San Francisco"

            # Step 4: Verify order appears in user's order history
            history_response = await async_test_client.get(
                "/orders",
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert history_response.status_code == 200

            history_data = history_response.json()
            assert history_data["total"] >= 1
            assert len(history_data["orders"]) >= 1

            # Find our order in the history
            created_order = next((o for o in history_data["orders"] if o["id"] == order_id), None)
            assert created_order is not None
            assert created_order["status"] == "PENDING"

    @pytest.mark.asyncio
    async def test_order_creation_flow_empty_cart_failure(
        self,
        async_test_client: AsyncClient,
        sample_order_data,
        mock_jwt_token,
        mock_empty_cart_response
    ):
        """Test that order creation fails gracefully when cart is empty."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth, \
             patch('src.clients.cart_client.CartClient.get_cart') as mock_get_cart:

            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}
            mock_get_cart.return_value = mock_empty_cart_response

            response = await async_test_client.post(
                "/orders",
                json=sample_order_data,
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 422
            error_data = response.json()
            assert "empty" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_order_creation_flow_product_unavailable(
        self,
        async_test_client: AsyncClient,
        sample_order_data,
        mock_jwt_token,
        mock_cart_response
    ):
        """Test order creation when a product becomes unavailable."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth, \
             patch('src.clients.cart_client.CartClient.get_cart') as mock_get_cart, \
             patch('src.clients.product_client.ProductClient.get_product_details') as mock_product:

            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}
            mock_get_cart.return_value = mock_cart_response

            # Mock product as unavailable
            mock_product.return_value = {"id": 2, "available": False}

            response = await async_test_client.post(
                "/orders",
                json=sample_order_data,
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 422
            error_data = response.json()
            assert "unavailable" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_order_creation_flow_service_failure_rollback(
        self,
        async_test_client: AsyncClient,
        sample_order_data,
        mock_jwt_token,
        mock_cart_response
    ):
        """Test that order creation handles service failures gracefully."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth, \
             patch('src.clients.cart_client.CartClient.get_cart') as mock_get_cart, \
             patch('src.clients.cart_client.CartClient.clear_cart') as mock_clear_cart:

            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}
            mock_get_cart.return_value = mock_cart_response
            # Simulate failure when trying to clear cart
            mock_clear_cart.side_effect = Exception("Cart service unavailable")

            response = await async_test_client.post(
                "/orders",
                json=sample_order_data,
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            # Should fail gracefully without creating incomplete order
            assert response.status_code == 503