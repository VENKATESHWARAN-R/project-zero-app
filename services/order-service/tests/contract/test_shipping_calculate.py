"""
Contract test for POST /shipping/calculate endpoint.

This test MUST FAIL until the endpoint is implemented.
Tests shipping cost calculations based on weight tiers.
"""

import pytest
from httpx import AsyncClient


class TestShippingCalculation:
    """Test cases for shipping cost calculation endpoint."""

    @pytest.mark.asyncio
    async def test_calculate_shipping_light_tier(self, async_test_client: AsyncClient):
        """Test shipping calculation for light items (≤1 lb)."""
        shipping_data = {
            "items": [
                {"weight": 0.5, "quantity": 1},
                {"weight": 0.3, "quantity": 1}
            ],
            "address": {
                "recipient_name": "John Doe",
                "address_line_1": "123 Main Street",
                "city": "San Francisco",
                "state_province": "CA",
                "postal_code": "94105",
                "country": "US"
            }
        }

        response = await async_test_client.post("/shipping/calculate", json=shipping_data)

        # This SHOULD FAIL until implementation exists
        assert response.status_code == 200

        data = response.json()
        assert "shipping_cost" in data
        assert "shipping_tier" in data
        assert "total_weight" in data

        # Total weight: 0.5 + 0.3 = 0.8 lbs (Light tier)
        assert data["total_weight"] == 0.8
        assert data["shipping_tier"] == "Light"
        assert data["shipping_cost"] == 5.99  # Light tier rate

    @pytest.mark.asyncio
    async def test_calculate_shipping_medium_tier(self, async_test_client: AsyncClient, sample_shipping_calculation_data):
        """Test shipping calculation for medium items (≤5 lb)."""
        response = await async_test_client.post("/shipping/calculate", json=sample_shipping_calculation_data)

        assert response.status_code == 200

        data = response.json()
        # Total weight: (0.5 * 2) + (1.2 * 1) = 2.2 lbs (Medium tier)
        assert data["total_weight"] == 2.2
        assert data["shipping_tier"] == "Medium"
        assert data["shipping_cost"] == 8.99  # Medium tier rate

    @pytest.mark.asyncio
    async def test_calculate_shipping_heavy_tier(self, async_test_client: AsyncClient):
        """Test shipping calculation for heavy items (≤20 lb)."""
        shipping_data = {
            "items": [
                {"weight": 8.5, "quantity": 2}  # 17 lbs total
            ],
            "address": {
                "recipient_name": "John Doe",
                "address_line_1": "123 Main Street",
                "city": "San Francisco",
                "state_province": "CA",
                "postal_code": "94105",
                "country": "US"
            }
        }

        response = await async_test_client.post("/shipping/calculate", json=shipping_data)

        assert response.status_code == 200

        data = response.json()
        assert data["total_weight"] == 17.0
        assert data["shipping_tier"] == "Heavy"
        assert data["shipping_cost"] == 15.99  # Heavy tier rate

    @pytest.mark.asyncio
    async def test_calculate_shipping_freight_tier(self, async_test_client: AsyncClient):
        """Test shipping calculation for freight items (>20 lb)."""
        shipping_data = {
            "items": [
                {"weight": 15.0, "quantity": 2}  # 30 lbs total
            ],
            "address": {
                "recipient_name": "John Doe",
                "address_line_1": "123 Main Street",
                "city": "San Francisco",
                "state_province": "CA",
                "postal_code": "94105",
                "country": "US"
            }
        }

        response = await async_test_client.post("/shipping/calculate", json=shipping_data)

        assert response.status_code == 200

        data = response.json()
        assert data["total_weight"] == 30.0
        assert data["shipping_tier"] == "Freight"
        assert data["shipping_cost"] == 25.99  # Freight tier rate

    @pytest.mark.asyncio
    async def test_calculate_shipping_invalid_data(self, async_test_client: AsyncClient):
        """Test shipping calculation with invalid data."""
        invalid_data = {
            "items": [],  # Empty items
            "address": {
                "recipient_name": "John Doe",
                "address_line_1": "123 Main Street",
                "city": "San Francisco",
                "state_province": "CA",
                "postal_code": "94105",
                "country": "US"
            }
        }

        response = await async_test_client.post("/shipping/calculate", json=invalid_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_shipping_negative_weight(self, async_test_client: AsyncClient):
        """Test shipping calculation with negative weight."""
        invalid_data = {
            "items": [
                {"weight": -1.0, "quantity": 1}
            ],
            "address": {
                "recipient_name": "John Doe",
                "address_line_1": "123 Main Street",
                "city": "San Francisco",
                "state_province": "CA",
                "postal_code": "94105",
                "country": "US"
            }
        }

        response = await async_test_client.post("/shipping/calculate", json=invalid_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_shipping_zero_quantity(self, async_test_client: AsyncClient):
        """Test shipping calculation with zero quantity."""
        invalid_data = {
            "items": [
                {"weight": 1.0, "quantity": 0}
            ],
            "address": {
                "recipient_name": "John Doe",
                "address_line_1": "123 Main Street",
                "city": "San Francisco",
                "state_province": "CA",
                "postal_code": "94105",
                "country": "US"
            }
        }

        response = await async_test_client.post("/shipping/calculate", json=invalid_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_shipping_invalid_address(self, async_test_client: AsyncClient):
        """Test shipping calculation with invalid address."""
        invalid_data = {
            "items": [
                {"weight": 1.0, "quantity": 1}
            ],
            "address": {
                "recipient_name": "",  # Empty name
                "address_line_1": "",  # Empty address
                "city": "",
                "state_province": "",
                "postal_code": "",
                "country": "INVALID"  # Invalid country code
            }
        }

        response = await async_test_client.post("/shipping/calculate", json=invalid_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_shipping_missing_required_fields(self, async_test_client: AsyncClient):
        """Test shipping calculation with missing required fields."""
        incomplete_data = {
            "items": [
                {"weight": 1.0}  # Missing quantity
            ]
        }

        response = await async_test_client.post("/shipping/calculate", json=incomplete_data)

        assert response.status_code == 422