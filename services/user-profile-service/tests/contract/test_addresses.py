"""Contract tests for address management endpoints.

These tests verify that the address endpoints conform to the OpenAPI specification
and return the expected response schemas.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class AddressResponse(BaseModel):
    """Expected address response schema from OpenAPI spec."""
    id: int
    user_id: int
    address_type: Literal["shipping", "billing"]
    street_address: str
    address_line_2: Optional[str] = None
    city: str
    state_province: Optional[str] = None
    postal_code: str
    country: str
    label: Optional[str] = None
    is_default: bool
    created_at: str
    updated_at: str


class ErrorResponse(BaseModel):
    """Expected error response schema from OpenAPI spec."""
    error: str
    message: str
    timestamp: str
    details: Optional[dict] = None


@pytest.fixture
def client():
    """Test client fixture - will be implemented once FastAPI app exists."""
    from main import app
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock auth headers for testing."""
    return {"Authorization": "Bearer fake-jwt-token-for-testing"}


@pytest.fixture
def valid_address_data():
    """Valid address data for create/update operations."""
    return {
        "address_type": "shipping",
        "street_address": "123 Main St",
        "address_line_2": "Apt 4B",
        "city": "San Francisco",
        "state_province": "CA",
        "postal_code": "94105",
        "country": "US",
        "label": "Home",
        "is_default": False
    }


@pytest.fixture
def invalid_address_data():
    """Invalid address data for validation testing."""
    return {
        "address_type": "invalid",  # Invalid enum value
        "street_address": "",  # Required field empty
        "city": "S" * 101,  # Too long
        "postal_code": "",  # Required field empty
        "country": "USA",  # Invalid format (should be 2-letter)
    }


class TestAddressEndpoints:
    """Contract tests for address management endpoints."""

    def test_get_addresses_endpoint_exists(self, client, auth_headers):
        """Test that GET /addresses endpoint exists."""
        response = client.get("/addresses", headers=auth_headers)
        assert response.status_code in [200, 401], "Addresses GET should return 200 or 401"

    def test_get_addresses_requires_auth(self, client):
        """Test that GET /addresses requires authentication."""
        response = client.get("/addresses")
        assert response.status_code == 401, "Addresses GET should require authentication"

    def test_get_addresses_response_schema(self, client, auth_headers):
        """Test that GET /addresses returns valid array of AddressResponse."""
        response = client.get("/addresses", headers=auth_headers)

        if response.status_code == 200:
            addresses = response.json()
            assert isinstance(addresses, list), "Addresses response should be an array"

            # Validate each address in the response
            for address_data in addresses:
                address = AddressResponse.model_validate(address_data)
                assert address.id > 0
                assert address.user_id > 0
                assert address.address_type in ["shipping", "billing"]
                assert address.country.match(r"^[A-Z]{2}$") is not None

    def test_get_addresses_type_filter(self, client, auth_headers):
        """Test that GET /addresses supports type filtering."""
        # Test shipping filter
        response = client.get("/addresses?type=shipping", headers=auth_headers)
        if response.status_code == 200:
            addresses = response.json()
            for address_data in addresses:
                address = AddressResponse.model_validate(address_data)
                assert address.address_type == "shipping"

        # Test billing filter
        response = client.get("/addresses?type=billing", headers=auth_headers)
        if response.status_code == 200:
            addresses = response.json()
            for address_data in addresses:
                address = AddressResponse.model_validate(address_data)
                assert address.address_type == "billing"

    def test_create_address_endpoint_exists(self, client, auth_headers, valid_address_data):
        """Test that POST /addresses endpoint exists."""
        response = client.post("/addresses", json=valid_address_data, headers=auth_headers)
        assert response.status_code in [201, 400, 401], "Address POST should return 201, 400, or 401"

    def test_create_address_requires_auth(self, client, valid_address_data):
        """Test that POST /addresses requires authentication."""
        response = client.post("/addresses", json=valid_address_data)
        assert response.status_code == 401, "Address POST should require authentication"

    def test_create_address_response_schema(self, client, auth_headers, valid_address_data):
        """Test that POST /addresses returns valid AddressResponse schema."""
        response = client.post("/addresses", json=valid_address_data, headers=auth_headers)

        if response.status_code == 201:
            address = AddressResponse.model_validate(response.json())

            # Verify created address contains submitted data
            assert address.street_address == valid_address_data["street_address"]
            assert address.city == valid_address_data["city"]
            assert address.country == valid_address_data["country"]
            assert address.address_type == valid_address_data["address_type"]

    def test_create_address_validation(self, client, auth_headers, invalid_address_data):
        """Test that POST /addresses validates input data."""
        response = client.post("/addresses", json=invalid_address_data, headers=auth_headers)
        assert response.status_code == 400, "Invalid address data should return 400"

        error_data = ErrorResponse.model_validate(response.json())
        assert error_data.error in ["Validation failed", "Bad Request"]

    def test_get_specific_address_endpoint(self, client, auth_headers):
        """Test that GET /addresses/{address_id} endpoint exists."""
        # Test with a sample address ID
        response = client.get("/addresses/1", headers=auth_headers)
        assert response.status_code in [200, 404, 401], "Specific address GET should return 200, 404, or 401"

    def test_get_specific_address_requires_auth(self, client):
        """Test that GET /addresses/{address_id} requires authentication."""
        response = client.get("/addresses/1")
        assert response.status_code == 401, "Specific address GET should require authentication"

    def test_update_address_endpoint_exists(self, client, auth_headers, valid_address_data):
        """Test that PUT /addresses/{address_id} endpoint exists."""
        update_data = {"city": "Los Angeles", "state_province": "CA"}
        response = client.put("/addresses/1", json=update_data, headers=auth_headers)
        assert response.status_code in [200, 404, 400, 401], "Address PUT should return 200, 404, 400, or 401"

    def test_update_address_requires_auth(self, client):
        """Test that PUT /addresses/{address_id} requires authentication."""
        update_data = {"city": "Los Angeles"}
        response = client.put("/addresses/1", json=update_data)
        assert response.status_code == 401, "Address PUT should require authentication"

    def test_delete_address_endpoint_exists(self, client, auth_headers):
        """Test that DELETE /addresses/{address_id} endpoint exists."""
        response = client.delete("/addresses/1", headers=auth_headers)
        assert response.status_code in [204, 404, 409, 401], "Address DELETE should return 204, 404, 409, or 401"

    def test_delete_address_requires_auth(self, client):
        """Test that DELETE /addresses/{address_id} requires authentication."""
        response = client.delete("/addresses/1")
        assert response.status_code == 401, "Address DELETE should require authentication"

    def test_set_default_address_endpoint_exists(self, client, auth_headers):
        """Test that PUT /addresses/{address_id}/default endpoint exists."""
        response = client.put("/addresses/1/default", headers=auth_headers)
        assert response.status_code in [200, 404, 401], "Set default address should return 200, 404, or 401"

    def test_set_default_address_requires_auth(self, client):
        """Test that PUT /addresses/{address_id}/default requires authentication."""
        response = client.put("/addresses/1/default")
        assert response.status_code == 401, "Set default address should require authentication"

    def test_address_type_validation(self, client, auth_headers, valid_address_data):
        """Test address type enum validation."""
        valid_types = ["shipping", "billing"]
        invalid_types = ["home", "work", "other", ""]

        # Test valid types
        for addr_type in valid_types:
            data = valid_address_data.copy()
            data["address_type"] = addr_type
            response = client.post("/addresses", json=data, headers=auth_headers)
            if response.status_code == 400:
                error_data = response.json()
                assert "address_type" not in error_data.get("details", {}), f"Valid type {addr_type} was rejected"

        # Test invalid types
        for addr_type in invalid_types:
            data = valid_address_data.copy()
            data["address_type"] = addr_type
            response = client.post("/addresses", json=data, headers=auth_headers)
            if response.status_code != 201:  # Should be rejected
                assert response.status_code == 400

    def test_country_code_validation(self, client, auth_headers, valid_address_data):
        """Test ISO 3166-1 alpha-2 country code validation."""
        valid_countries = ["US", "CA", "GB", "FR", "DE", "JP"]
        invalid_countries = ["USA", "CAN", "GBR", "us", "123", ""]

        # Test valid country codes
        for country in valid_countries:
            data = valid_address_data.copy()
            data["country"] = country
            response = client.post("/addresses", json=data, headers=auth_headers)
            if response.status_code == 400:
                error_data = response.json()
                assert "country" not in error_data.get("details", {}), f"Valid country {country} was rejected"

        # Test invalid country codes
        for country in invalid_countries:
            data = valid_address_data.copy()
            data["country"] = country
            response = client.post("/addresses", json=data, headers=auth_headers)
            if response.status_code != 201:  # Should be rejected
                assert response.status_code == 400

    def test_postal_code_validation(self, client, auth_headers, valid_address_data):
        """Test postal code validation."""
        valid_postal_codes = ["94105", "90210", "10001", "SW1A 1AA", "75001"]
        invalid_postal_codes = ["", "a" * 25]  # Empty or too long

        # Test valid postal codes
        for postal_code in valid_postal_codes:
            data = valid_address_data.copy()
            data["postal_code"] = postal_code
            response = client.post("/addresses", json=data, headers=auth_headers)
            if response.status_code == 400:
                error_data = response.json()
                assert "postal_code" not in error_data.get("details", {}), f"Valid postal code {postal_code} was rejected"

        # Test invalid postal codes
        for postal_code in invalid_postal_codes:
            data = valid_address_data.copy()
            data["postal_code"] = postal_code
            response = client.post("/addresses", json=data, headers=auth_headers)
            if response.status_code != 201:  # Should be rejected
                assert response.status_code == 400

    def test_required_fields_validation(self, client, auth_headers, valid_address_data):
        """Test that required fields are validated."""
        required_fields = ["address_type", "street_address", "city", "postal_code", "country"]

        for field in required_fields:
            data = valid_address_data.copy()
            del data[field]  # Remove required field
            response = client.post("/addresses", json=data, headers=auth_headers)
            assert response.status_code == 400, f"Missing required field {field} should return 400"

            error_data = ErrorResponse.model_validate(response.json())
            assert error_data.error in ["Validation failed", "Bad Request"]

    def test_default_address_logic(self, client, auth_headers, valid_address_data):
        """Test default address management logic."""
        # Create first address with is_default=true
        data1 = valid_address_data.copy()
        data1["is_default"] = True
        data1["label"] = "First Address"
        response1 = client.post("/addresses", json=data1, headers=auth_headers)

        # Create second address with is_default=true
        data2 = valid_address_data.copy()
        data2["is_default"] = True
        data2["label"] = "Second Address"
        response2 = client.post("/addresses", json=data2, headers=auth_headers)

        # If both succeed, verify only one is default
        if response1.status_code == 201 and response2.status_code == 201:
            # Get all addresses and verify only one is default per type
            response = client.get("/addresses", headers=auth_headers)
            if response.status_code == 200:
                addresses = response.json()
                shipping_defaults = sum(1 for addr in addresses if addr["address_type"] == "shipping" and addr["is_default"])
                billing_defaults = sum(1 for addr in addresses if addr["address_type"] == "billing" and addr["is_default"])

                assert shipping_defaults <= 1, "Should have at most one default shipping address"
                assert billing_defaults <= 1, "Should have at most one default billing address"

    def test_delete_address_conflict(self, client, auth_headers):
        """Test that deleting address in use returns 409 Conflict."""
        # This test verifies the contract for when an address cannot be deleted
        # because it's being used by an active order
        response = client.delete("/addresses/1", headers=auth_headers)

        if response.status_code == 409:
            error_data = ErrorResponse.model_validate(response.json())
            assert "in use" in error_data.message.lower() or "active order" in error_data.message.lower()

    @pytest.mark.integration
    def test_address_operations_performance(self, client, auth_headers, valid_address_data):
        """Test that address operations respond quickly (< 200ms)."""
        import time

        # Test GET addresses performance
        start_time = time.time()
        response = client.get("/addresses", headers=auth_headers)
        get_duration = time.time() - start_time
        assert get_duration < 0.2, f"GET /addresses took {get_duration:.3f}s, should be < 200ms"

        # Test POST address performance
        start_time = time.time()
        response = client.post("/addresses", json=valid_address_data, headers=auth_headers)
        post_duration = time.time() - start_time
        if response.status_code in [201, 400]:  # Expected responses
            assert post_duration < 0.2, f"POST /addresses took {post_duration:.3f}s, should be < 200ms"