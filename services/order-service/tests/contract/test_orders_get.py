"""
Contract test for GET /orders endpoint.

This test MUST FAIL until the endpoint is implemented.
Tests order history retrieval with pagination and filtering.
"""

import pytest
from unittest.mock import patch
from httpx import AsyncClient


class TestGetOrderHistory:
    """Test cases for order history endpoint."""

    @pytest.mark.asyncio
    async def test_get_order_history_success(self, async_test_client: AsyncClient, mock_jwt_token, created_order):
        """Test successful order history retrieval."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}

            response = await async_test_client.get(
                "/orders",
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            # This SHOULD FAIL until implementation exists
            assert response.status_code == 200

            data = response.json()
            assert "orders" in data
            assert "total" in data
            assert "limit" in data
            assert "offset" in data

            # Should return the created order
            orders = data["orders"]
            assert len(orders) == 1
            assert orders[0]["id"] == created_order.id
            assert orders[0]["order_number"] == created_order.order_number
            assert orders[0]["status"] == created_order.status.value
            assert orders[0]["user_id"] == created_order.user_id

    @pytest.mark.asyncio
    async def test_get_order_history_with_pagination(self, async_test_client: AsyncClient, mock_jwt_token):
        """Test order history with pagination parameters."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}

            response = await async_test_client.get(
                "/orders?limit=10&offset=0",
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 200

            data = response.json()
            assert data["limit"] == 10
            assert data["offset"] == 0

    @pytest.mark.asyncio
    async def test_get_order_history_with_status_filter(self, async_test_client: AsyncClient, mock_jwt_token):
        """Test order history with status filtering."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}

            response = await async_test_client.get(
                "/orders?status=PENDING",
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_order_history_unauthorized(self, async_test_client: AsyncClient):
        """Test order history fails without authentication."""
        response = await async_test_client.get("/orders")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_order_history_invalid_status_filter(self, async_test_client: AsyncClient, mock_jwt_token):
        """Test order history with invalid status filter."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}

            response = await async_test_client.get(
                "/orders?status=INVALID_STATUS",
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_order_history_invalid_pagination(self, async_test_client: AsyncClient, mock_jwt_token):
        """Test order history with invalid pagination parameters."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 42, "email": "test@example.com", "role": "user"}

            # Test negative limit
            response = await async_test_client.get(
                "/orders?limit=-1",
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 422

            # Test limit too large
            response = await async_test_client.get(
                "/orders?limit=1000",
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 422

            # Test negative offset
            response = await async_test_client.get(
                "/orders?offset=-1",
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_order_history_empty_results(self, async_test_client: AsyncClient, mock_jwt_token):
        """Test order history when user has no orders."""
        with patch('src.clients.auth_client.AuthClient.verify_token') as mock_auth:
            mock_auth.return_value = {"user_id": 999, "email": "noorders@example.com", "role": "user"}

            response = await async_test_client.get(
                "/orders",
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 200

            data = response.json()
            assert data["orders"] == []
            assert data["total"] == 0