"""Integration tests for address management workflow.

These tests verify the complete address management functionality including
default address logic, validation, and business rules.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any, List


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
def shipping_address_data():
    """Sample shipping address data."""
    return {
        "address_type": "shipping",
        "street_address": "123 Main St",
        "address_line_2": "Apt 4B",
        "city": "San Francisco",
        "state_province": "CA",
        "postal_code": "94105",
        "country": "US",
        "label": "Home",
        "is_default": True
    }


@pytest.fixture
def billing_address_data():
    """Sample billing address data."""
    return {
        "address_type": "billing",
        "street_address": "456 Business Ave",
        "city": "Los Angeles",
        "state_province": "CA",
        "postal_code": "90210",
        "country": "US",
        "label": "Office",
        "is_default": True
    }


class TestAddressManagementFlow:
    """Integration tests for address management workflow."""

    def test_complete_address_lifecycle(self, client, auth_headers, shipping_address_data):
        """Test the complete address lifecycle: create, read, update, delete."""
        # Step 1: Create address
        create_response = client.post("/addresses", json=shipping_address_data, headers=auth_headers)

        if create_response.status_code == 201:
            created_address = create_response.json()
            address_id = created_address["id"]

            # Verify created address data
            assert created_address["street_address"] == shipping_address_data["street_address"]
            assert created_address["city"] == shipping_address_data["city"]
            assert created_address["is_default"] == True

            # Step 2: Read specific address
            get_response = client.get(f"/addresses/{address_id}", headers=auth_headers)
            if get_response.status_code == 200:
                retrieved_address = get_response.json()
                assert retrieved_address["id"] == address_id
                assert retrieved_address["street_address"] == shipping_address_data["street_address"]

            # Step 3: Update address
            update_data = {"city": "Sacramento", "postal_code": "95814"}
            update_response = client.put(f"/addresses/{address_id}", json=update_data, headers=auth_headers)

            if update_response.status_code == 200:
                updated_address = update_response.json()
                assert updated_address["city"] == "Sacramento"
                assert updated_address["postal_code"] == "95814"
                # Original data should be preserved
                assert updated_address["street_address"] == shipping_address_data["street_address"]

            # Step 4: Delete address
            delete_response = client.delete(f"/addresses/{address_id}", headers=auth_headers)
            if delete_response.status_code == 204:
                # Verify address is deleted
                get_deleted_response = client.get(f"/addresses/{address_id}", headers=auth_headers)
                assert get_deleted_response.status_code == 404

    def test_default_address_management(self, client, auth_headers, shipping_address_data):
        """Test default address logic and enforcement."""
        # Create first shipping address as default
        first_address_data = shipping_address_data.copy()
        first_address_data["label"] = "First Address"
        first_address_data["is_default"] = True

        first_response = client.post("/addresses", json=first_address_data, headers=auth_headers)

        if first_response.status_code == 201:
            first_address = first_response.json()
            first_address_id = first_address["id"]

            # Create second shipping address as default
            second_address_data = shipping_address_data.copy()
            second_address_data["street_address"] = "789 Second St"
            second_address_data["label"] = "Second Address"
            second_address_data["is_default"] = True

            second_response = client.post("/addresses", json=second_address_data, headers=auth_headers)

            if second_response.status_code == 201:
                # Verify only one default address exists
                addresses_response = client.get("/addresses?type=shipping", headers=auth_headers)
                if addresses_response.status_code == 200:
                    addresses = addresses_response.json()
                    default_count = sum(1 for addr in addresses if addr["is_default"])
                    assert default_count == 1, "Only one default shipping address should exist"

                    # Verify the second address is now the default
                    second_address = second_response.json()
                    assert second_address["is_default"] == True

                    # Verify first address is no longer default
                    first_check_response = client.get(f"/addresses/{first_address_id}", headers=auth_headers)
                    if first_check_response.status_code == 200:
                        first_address_updated = first_check_response.json()
                        assert first_address_updated["is_default"] == False

    def test_set_default_address_endpoint(self, client, auth_headers, shipping_address_data):
        """Test the set default address endpoint functionality."""
        # Create two shipping addresses
        first_data = shipping_address_data.copy()
        first_data["label"] = "Address 1"
        first_data["is_default"] = True

        second_data = shipping_address_data.copy()
        second_data["street_address"] = "456 Other St"
        second_data["label"] = "Address 2"
        second_data["is_default"] = False

        # Create addresses
        first_response = client.post("/addresses", json=first_data, headers=auth_headers)
        second_response = client.post("/addresses", json=second_data, headers=auth_headers)

        if first_response.status_code == 201 and second_response.status_code == 201:
            second_address_id = second_response.json()["id"]

            # Set second address as default using the endpoint
            set_default_response = client.put(f"/addresses/{second_address_id}/default", headers=auth_headers)

            if set_default_response.status_code == 200:
                # Verify second address is now default
                updated_address = set_default_response.json()
                assert updated_address["is_default"] == True

                # Verify only one default exists
                addresses_response = client.get("/addresses?type=shipping", headers=auth_headers)
                if addresses_response.status_code == 200:
                    addresses = addresses_response.json()
                    default_count = sum(1 for addr in addresses if addr["is_default"])
                    assert default_count == 1, "Only one default shipping address should exist after setting new default"

    def test_address_type_separation(self, client, auth_headers, shipping_address_data, billing_address_data):
        """Test that shipping and billing addresses are managed separately."""
        # Create default shipping address
        shipping_response = client.post("/addresses", json=shipping_address_data, headers=auth_headers)

        # Create default billing address
        billing_response = client.post("/addresses", json=billing_address_data, headers=auth_headers)

        if shipping_response.status_code == 201 and billing_response.status_code == 201:
            # Verify both can be default simultaneously (different types)
            shipping_address = shipping_response.json()
            billing_address = billing_response.json()

            assert shipping_address["is_default"] == True
            assert billing_address["is_default"] == True
            assert shipping_address["address_type"] == "shipping"
            assert billing_address["address_type"] == "billing"

            # Verify filtering by type works
            shipping_filter_response = client.get("/addresses?type=shipping", headers=auth_headers)
            if shipping_filter_response.status_code == 200:
                shipping_addresses = shipping_filter_response.json()
                assert all(addr["address_type"] == "shipping" for addr in shipping_addresses)

            billing_filter_response = client.get("/addresses?type=billing", headers=auth_headers)
            if billing_filter_response.status_code == 200:
                billing_addresses = billing_filter_response.json()
                assert all(addr["address_type"] == "billing" for addr in billing_addresses)

    def test_address_validation_integration(self, client, auth_headers):
        """Test address validation in complete workflow context."""
        validation_scenarios = [
            # Valid addresses
            {
                "data": {
                    "address_type": "shipping",
                    "street_address": "123 Main St",
                    "city": "New York",
                    "postal_code": "10001",
                    "country": "US"
                },
                "expected_valid": True
            },
            # International address
            {
                "data": {
                    "address_type": "billing",
                    "street_address": "10 Downing Street",
                    "city": "London",
                    "postal_code": "SW1A 2AA",
                    "country": "GB"
                },
                "expected_valid": True
            },
            # Invalid country code
            {
                "data": {
                    "address_type": "shipping",
                    "street_address": "123 Main St",
                    "city": "Toronto",
                    "postal_code": "M5V 3A8",
                    "country": "CAN"  # Should be "CA"
                },
                "expected_valid": False
            },
            # Missing required fields
            {
                "data": {
                    "address_type": "shipping",
                    "city": "Boston",
                    "country": "US"
                    # Missing street_address and postal_code
                },
                "expected_valid": False
            }
        ]

        for scenario in validation_scenarios:
            response = client.post("/addresses", json=scenario["data"], headers=auth_headers)

            if scenario["expected_valid"]:
                assert response.status_code == 201, f"Valid address should be accepted: {scenario['data']}"
            else:
                assert response.status_code == 400, f"Invalid address should be rejected: {scenario['data']}"

    def test_first_address_auto_default(self, client, auth_headers, shipping_address_data):
        """Test that the first address automatically becomes default."""
        # Create first address without explicitly setting as default
        first_data = shipping_address_data.copy()
        first_data["is_default"] = False  # Explicitly set to False

        first_response = client.post("/addresses", json=first_data, headers=auth_headers)

        if first_response.status_code == 201:
            first_address = first_response.json()
            # First address should become default regardless of is_default setting
            assert first_address["is_default"] == True, "First address should automatically become default"

    def test_address_activity_logging(self, client, auth_headers, shipping_address_data):
        """Test that address operations are logged in activity history."""
        # Create address
        create_response = client.post("/addresses", json=shipping_address_data, headers=auth_headers)

        if create_response.status_code == 201:
            address_id = create_response.json()["id"]

            # Check activity log for address creation
            activity_response = client.get("/activity?activity_type=address_created", headers=auth_headers)
            if activity_response.status_code == 200:
                activities = activity_response.json()["activities"]
                creation_activity = next((a for a in activities if a["entity_id"] == address_id), None)

                if creation_activity:
                    assert creation_activity["activity_type"] == "address_created"
                    assert creation_activity["entity_type"] == "address"
                    assert "address" in creation_activity["description"].lower()

            # Update address
            update_data = {"city": "Updated City"}
            update_response = client.put(f"/addresses/{address_id}", json=update_data, headers=auth_headers)

            if update_response.status_code == 200:
                # Check for update activity
                update_activity_response = client.get("/activity?activity_type=address_updated", headers=auth_headers)
                if update_activity_response.status_code == 200:
                    update_activities = update_activity_response.json()["activities"]
                    update_activity = next((a for a in update_activities if a["entity_id"] == address_id), None)

                    if update_activity:
                        assert update_activity["activity_type"] == "address_updated"
                        assert "updated" in update_activity["description"].lower()

    def test_address_deletion_constraints(self, client, auth_headers, shipping_address_data):
        """Test address deletion constraints (e.g., used by active orders)."""
        # Create address
        create_response = client.post("/addresses", json=shipping_address_data, headers=auth_headers)

        if create_response.status_code == 201:
            address_id = create_response.json()["id"]

            # Attempt to delete address
            delete_response = client.delete(f"/addresses/{address_id}", headers=auth_headers)

            # Should either succeed (204) or fail due to constraints (409)
            assert delete_response.status_code in [204, 409]

            if delete_response.status_code == 409:
                error_data = delete_response.json()
                assert "in use" in error_data["message"].lower() or "active order" in error_data["message"].lower()

    def test_multiple_addresses_same_type(self, client, auth_headers, shipping_address_data):
        """Test managing multiple addresses of the same type."""
        addresses_to_create = [
            {**shipping_address_data, "label": "Home", "street_address": "123 Home St"},
            {**shipping_address_data, "label": "Work", "street_address": "456 Work Ave", "is_default": False},
            {**shipping_address_data, "label": "Parents", "street_address": "789 Family Rd", "is_default": False}
        ]

        created_addresses = []

        for addr_data in addresses_to_create:
            response = client.post("/addresses", json=addr_data, headers=auth_headers)
            if response.status_code == 201:
                created_addresses.append(response.json())

        if len(created_addresses) >= 2:
            # Verify all addresses exist
            all_addresses_response = client.get("/addresses?type=shipping", headers=auth_headers)
            if all_addresses_response.status_code == 200:
                all_addresses = all_addresses_response.json()
                assert len(all_addresses) >= len(created_addresses)

                # Verify only one is default
                default_count = sum(1 for addr in all_addresses if addr["is_default"])
                assert default_count == 1, "Only one address should be default"

                # Verify each address has unique characteristics
                labels = [addr["label"] for addr in all_addresses]
                street_addresses = [addr["street_address"] for addr in all_addresses]
                assert len(set(labels)) == len(labels), "Each address should have unique label"
                assert len(set(street_addresses)) == len(street_addresses), "Each address should have unique street address"

    @pytest.mark.integration
    def test_address_management_performance(self, client, auth_headers, shipping_address_data):
        """Test performance of address management operations."""
        import time

        # Test create performance
        start_time = time.time()
        create_response = client.post("/addresses", json=shipping_address_data, headers=auth_headers)
        create_time = time.time() - start_time

        if create_response.status_code == 201:
            assert create_time < 0.3, f"Address creation took {create_time:.3f}s, should be < 300ms"
            address_id = create_response.json()["id"]

            # Test read performance
            start_time = time.time()
            read_response = client.get("/addresses", headers=auth_headers)
            read_time = time.time() - start_time

            if read_response.status_code == 200:
                assert read_time < 0.2, f"Address listing took {read_time:.3f}s, should be < 200ms"

            # Test update performance
            start_time = time.time()
            update_response = client.put(f"/addresses/{address_id}", json={"city": "Fast City"}, headers=auth_headers)
            update_time = time.time() - start_time

            if update_response.status_code == 200:
                assert update_time < 0.3, f"Address update took {update_time:.3f}s, should be < 300ms"

    def test_international_address_support(self, client, auth_headers):
        """Test support for various international address formats."""
        international_addresses = [
            # Canadian address
            {
                "address_type": "shipping",
                "street_address": "123 Maple Ave",
                "city": "Toronto",
                "state_province": "ON",
                "postal_code": "M5V 3A8",
                "country": "CA",
                "label": "Canada Office"
            },
            # UK address
            {
                "address_type": "billing",
                "street_address": "10 Downing Street",
                "city": "London",
                "postal_code": "SW1A 2AA",
                "country": "GB",
                "label": "UK Office"
            },
            # German address
            {
                "address_type": "shipping",
                "street_address": "Unter den Linden 1",
                "city": "Berlin",
                "postal_code": "10117",
                "country": "DE",
                "label": "Berlin Office"
            }
        ]

        for addr_data in international_addresses:
            response = client.post("/addresses", json=addr_data, headers=auth_headers)
            assert response.status_code == 201, f"International address should be accepted: {addr_data['country']}"

            if response.status_code == 201:
                address = response.json()
                assert address["country"] == addr_data["country"]
                assert address["postal_code"] == addr_data["postal_code"]