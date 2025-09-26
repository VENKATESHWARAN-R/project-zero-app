"""
Contract test for GET /orders/{orderId} endpoint.

This test MUST FAIL until the endpoint is implemented.
Tests detailed order retrieval with items and shipping address.
"""

import pytest
from unittest.mock import patch
from httpx import AsyncClient


class TestGetOrderDetails:
    """Test cases for order detail endpoint."""

    @pytest.mark.asyncio
    async def test_get_order_details_success(self, async_test_client: AsyncClient, mock_jwt_token, created_order):
        """Test successful order details retrieval."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}

            response = await async_test_client.get(
                f"/orders/{created_order.id}",
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            # This SHOULD FAIL until implementation exists
            assert response.status_code == 200

            data = response.json()
            # Verify order details
            assert data["id"] == created_order.id
            assert data["order_number"] == created_order.order_number
            assert data["user_id"] == created_order.user_id
            assert data["status"] == created_order.status.value
            assert float(data["subtotal"]) == float(created_order.subtotal)
            assert float(data["total"]) == float(created_order.total)

            # Verify order items are included
            assert "items" in data
            assert len(data["items"]) == 2
            items = data["items"]
            assert items[0]["product_name"] == "Test Product 1"
            assert items[0]["quantity"] == 2
            assert items[1]["product_name"] == "Test Product 2"
            assert items[1]["quantity"] == 1

            # Verify shipping address is included
            assert "shipping_address" in data
            shipping = data["shipping_address"]
            assert shipping["recipient_name"] == "John Doe"
            assert shipping["address_line_1"] == "123 Main Street"
            assert shipping["city"] == "San Francisco"

    @pytest.mark.asyncio
    async def test_get_order_details_unauthorized(self, async_test_client: AsyncClient, created_order):
        """Test order details fails without authentication."""
        response = await async_test_client.get(f"/orders/{created_order.id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_order_details_forbidden(self, async_test_client: AsyncClient, mock_jwt_token, created_order):
        """Test order details fails when accessing another user's order."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            # Different user ID than the order owner (42)
            mock_auth.return_value = {"user_id": 999, "email": "other@example.com", "role": "user"}

            response = await async_test_client.get(
                f"/orders/{created_order.id}",
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_order_details_not_found(self, async_test_client: AsyncClient, mock_jwt_token):
        """Test order details returns 404 for non-existent order."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}

            response = await async_test_client.get(
                "/orders/99999",
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_order_details_invalid_order_id(self, async_test_client: AsyncClient, mock_jwt_token):
        """Test order details with invalid order ID format."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}

            response = await async_test_client.get(
                "/orders/invalid-id",
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_order_details_admin_can_access_any_order(self, async_test_client: AsyncClient, mock_admin_jwt_token, created_order):
        """Test that admin users can access any order details."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 1, "email": "admin@example.com", "role": "admin"}

            response = await async_test_client.get(
                f"/orders/{created_order.id}",
                headers={"Authorization": f"Bearer {mock_admin_jwt_token}"}
            )

            # Admin should be able to access any order
            assert response.status_code == 200

            data = response.json()
            assert data["id"] == created_order.id