"""
Contract test for GET /admin/orders endpoint.

This test MUST FAIL until the endpoint is implemented.
Tests admin order management with cross-user access.
"""

import pytest
from unittest.mock import patch
from httpx import AsyncClient


class TestAdminOrderManagement:
    """Test cases for admin order management endpoint."""

    @pytest.mark.asyncio
    async def test_admin_get_all_orders_success(self, async_test_client: AsyncClient, mock_admin_jwt_token, created_order):
        """Test successful admin order retrieval across all users."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 1, "email": "admin@example.com", "role": "admin"}

            response = await async_test_client.get(
                "/admin/orders",
                headers={"Authorization": f"Bearer {mock_admin_jwt_token}"}
            )

            # This SHOULD FAIL until implementation exists
            assert response.status_code == 200

            data = response.json()
            assert "orders" in data
            assert "total" in data
            assert "limit" in data
            assert "offset" in data

            # Should return orders from all users
            orders = data["orders"]
            assert len(orders) >= 1

            # Check that user email is included for admin view
            order = orders[0]
            assert order["id"] == created_order.id
            assert "user_email" in order  # Admin-specific field

    @pytest.mark.asyncio
    async def test_admin_get_orders_with_user_filter(self, async_test_client: AsyncClient, mock_admin_jwt_token):
        """Test admin order retrieval with user ID filtering."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 1, "email": "admin@example.com", "role": "admin"}

            response = await async_test_client.get(
                "/admin/orders?userId=42",
                headers={"Authorization": f"Bearer {mock_admin_jwt_token}"}
            )

            assert response.status_code == 200

            data = response.json()
            # All orders should belong to user 42
            for order in data["orders"]:
                assert order["user_id"] == 42

    @pytest.mark.asyncio
    async def test_admin_get_orders_with_status_filter(self, async_test_client: AsyncClient, mock_admin_jwt_token):
        """Test admin order retrieval with status filtering."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 1, "email": "admin@example.com", "role": "admin"}

            response = await async_test_client.get(
                "/admin/orders?status=PENDING",
                headers={"Authorization": f"Bearer {mock_admin_jwt_token}"}
            )

            assert response.status_code == 200

            data = response.json()
            # All orders should have PENDING status
            for order in data["orders"]:
                assert order["status"] == "PENDING"

    @pytest.mark.asyncio
    async def test_admin_get_orders_unauthorized(self, async_test_client: AsyncClient):
        """Test admin orders fails without authentication."""
        response = await async_test_client.get("/admin/orders")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_admin_get_orders_forbidden_for_regular_user(self, async_test_client: AsyncClient, mock_jwt_token):
        """Test admin orders fails for regular user."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}

            response = await async_test_client.get(
                "/admin/orders",
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_get_orders_with_pagination(self, async_test_client: AsyncClient, mock_admin_jwt_token):
        """Test admin order retrieval with pagination."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 1, "email": "admin@example.com", "role": "admin"}

            response = await async_test_client.get(
                "/admin/orders?limit=25&offset=10",
                headers={"Authorization": f"Bearer {mock_admin_jwt_token}"}
            )

            assert response.status_code == 200

            data = response.json()
            assert data["limit"] == 25
            assert data["offset"] == 10

    @pytest.mark.asyncio
    async def test_admin_get_orders_invalid_pagination(self, async_test_client: AsyncClient, mock_admin_jwt_token):
        """Test admin orders with invalid pagination parameters."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 1, "email": "admin@example.com", "role": "admin"}

            # Test limit too large
            response = await async_test_client.get(
                "/admin/orders?limit=1000",
                headers={"Authorization": f"Bearer {mock_admin_jwt_token}"}
            )

            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_admin_get_orders_invalid_user_filter(self, async_test_client: AsyncClient, mock_admin_jwt_token):
        """Test admin orders with invalid user ID filter."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 1, "email": "admin@example.com", "role": "admin"}

            response = await async_test_client.get(
                "/admin/orders?userId=invalid",
                headers={"Authorization": f"Bearer {mock_admin_jwt_token}"}
            )

            assert response.status_code == 422