"""
Contract test for POST /orders endpoint.

This test MUST FAIL until the endpoint is implemented.
Tests order creation from cart contents.
"""

import pytest
from unittest.mock import patch, Mock
from httpx import AsyncClient


class TestCreateOrder:
    """Test cases for order creation endpoint."""

    @pytest.mark.asyncio
    async def test_create_order_success(self, async_test_client: AsyncClient, sample_order_data, mock_jwt_token, mock_cart_response):
        """Test successful order creation from cart."""
        # Mock external service calls
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth, \
             patch('src.clients.cart_client.CartClient.get_cart') as mock_get_cart, \
             patch('src.clients.cart_client.CartClient.clear_cart') as mock_clear_cart, \
             patch('src.clients.product_client.ProductClient.get_product_details') as mock_product:

            # Setup mocks
            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}
            mock_get_cart.return_value = mock_cart_response
            mock_clear_cart.return_value = {"success": True}
            mock_product.return_value = {"id": 2, "name": "Test Product", "available": True}

            # Make request
            response = await async_test_client.post(
                "/orders",
                json=sample_order_data,
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            # Assertions - This SHOULD FAIL until implementation exists
            assert response.status_code == 201

            data = response.json()
            assert "id" in data
            assert "order_number" in data
            assert data["user_id"] == 42
            assert data["status"] == "PENDING"
            assert "subtotal" in data
            assert "tax_amount" in data
            assert "shipping_cost" in data
            assert "total" in data
            assert data["currency"] == "USD"
            assert "created_at" in data
            assert "updated_at" in data

            # Verify cart was cleared
            mock_clear_cart.assert_called_once_with(42)

    @pytest.mark.asyncio
    async def test_create_order_empty_cart(self, async_test_client: AsyncClient, sample_order_data, mock_jwt_token, mock_empty_cart_response):
        """Test order creation fails with empty cart."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth, \
             patch('src.clients.cart_client.CartClient.get_cart') as mock_get_cart:

            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}
            mock_get_cart.return_value = mock_empty_cart_response

            response = await async_test_client.post(
                "/orders",
                json=sample_order_data,
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            # Should fail with 422 - Cart is empty
            assert response.status_code == 422
            assert "empty" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_order_unauthorized(self, async_test_client: AsyncClient, sample_order_data):
        """Test order creation fails without authentication."""
        response = await async_test_client.post("/orders", json=sample_order_data)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_order_invalid_data(self, async_test_client: AsyncClient, mock_jwt_token):
        """Test order creation fails with invalid shipping address."""
        invalid_data = {
            "shipping_address": {
                "recipient_name": "",  # Invalid - empty name
                "address_line_1": "",  # Invalid - empty address
                "city": "",
                "state_province": "",
                "postal_code": "",
                "country": "INVALID"  # Invalid country code
            }
        }

        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}

            response = await async_test_client.post(
                "/orders",
                json=invalid_data,
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_order_service_unavailable(self, async_test_client: AsyncClient, sample_order_data, mock_jwt_token):
        """Test order creation fails when cart service is unavailable."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth, \
             patch('src.clients.cart_client.CartClient.get_cart') as mock_get_cart:

            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}
            mock_get_cart.side_effect = Exception("Cart service unavailable")

            response = await async_test_client.post(
                "/orders",
                json=sample_order_data,
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            # Should return 503 Service Unavailable
            assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_create_order_calculates_totals_correctly(self, async_test_client: AsyncClient, sample_order_data, mock_jwt_token, mock_cart_response):
        """Test that order creation calculates totals correctly."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth, \
             patch('src.clients.cart_client.CartClient.get_cart') as mock_get_cart, \
             patch('src.clients.cart_client.CartClient.clear_cart') as mock_clear_cart, \
             patch('src.services.tax_service.TaxService.calculate_tax') as mock_tax, \
             patch('src.services.shipping_service.ShippingService.calculate_shipping_cost') as mock_shipping:

            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}
            mock_get_cart.return_value = mock_cart_response
            mock_clear_cart.return_value = {"success": True}
            mock_tax.return_value = 7.65  # 8.5% of 89.97
            mock_shipping.return_value = 8.99

            response = await async_test_client.post(
                "/orders",
                json=sample_order_data,
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 201

            data = response.json()
            assert data["subtotal"] == 89.97
            assert data["tax_amount"] == 7.65
            assert data["shipping_cost"] == 8.99
            assert data["total"] == 106.61  # 89.97 + 7.65 + 8.99