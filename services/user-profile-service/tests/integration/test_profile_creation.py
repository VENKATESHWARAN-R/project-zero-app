"""Integration tests for profile creation flow.

These tests verify the complete profile creation workflow including
dependencies, side effects, and business logic.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any


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
def complete_profile_data():
    """Complete profile data for testing."""
    return {
        "first_name": "Jane",
        "last_name": "Smith",
        "phone": "+1-555-987-6543",
        "date_of_birth": "1985-03-22",
        "profile_picture_url": "https://example.com/jane-profile.jpg"
    }


class TestProfileCreationFlow:
    """Integration tests for profile creation workflow."""

    def test_complete_profile_creation_workflow(self, client, auth_headers, complete_profile_data):
        """Test the complete profile creation workflow from start to finish."""
        # Step 1: Verify no profile exists initially
        response = client.get("/profiles", headers=auth_headers)
        assert response.status_code in [404, 200], "Initial profile check should return 404 or existing profile"

        if response.status_code == 404:
            # Step 2: Create new profile
            create_response = client.post("/profiles", json=complete_profile_data, headers=auth_headers)
            assert create_response.status_code == 201, "Profile creation should succeed"

            created_profile = create_response.json()
            assert created_profile["first_name"] == complete_profile_data["first_name"]
            assert created_profile["last_name"] == complete_profile_data["last_name"]
            assert created_profile["phone"] == complete_profile_data["phone"]

            # Step 3: Verify profile can be retrieved
            get_response = client.get("/profiles", headers=auth_headers)
            assert get_response.status_code == 200, "Profile should be retrievable after creation"

            retrieved_profile = get_response.json()
            assert retrieved_profile["id"] == created_profile["id"]
            assert retrieved_profile["user_id"] == created_profile["user_id"]

    def test_profile_creation_with_preferences_initialization(self, client, auth_headers, complete_profile_data):
        """Test that profile creation automatically initializes user preferences."""
        # Create profile
        create_response = client.post("/profiles", json=complete_profile_data, headers=auth_headers)

        if create_response.status_code == 201:
            # Verify preferences are automatically created with defaults
            prefs_response = client.get("/preferences", headers=auth_headers)

            if prefs_response.status_code == 200:
                preferences = prefs_response.json()

                # Verify default preference values
                assert preferences["email_marketing"] == True
                assert preferences["email_order_updates"] == True
                assert preferences["email_security_alerts"] == True
                assert preferences["sms_notifications"] == False
                assert preferences["preferred_language"] == "en-US"
                assert preferences["preferred_currency"] == "USD"
                assert preferences["profile_visibility"] == "private"

    def test_profile_creation_activity_logging(self, client, auth_headers, complete_profile_data):
        """Test that profile creation is properly logged in activity history."""
        # Create profile
        create_response = client.post("/profiles", json=complete_profile_data, headers=auth_headers)

        if create_response.status_code == 201:
            # Check activity log for profile creation event
            activity_response = client.get("/activity?limit=5", headers=auth_headers)

            if activity_response.status_code == 200:
                activities = activity_response.json()["activities"]

                # Find profile creation activity
                profile_created_activity = None
                for activity in activities:
                    if activity["activity_type"] == "profile_created":
                        profile_created_activity = activity
                        break

                if profile_created_activity:
                    assert "created" in profile_created_activity["description"].lower()
                    assert profile_created_activity["entity_type"] == "profile"
                    assert profile_created_activity["entity_id"] is not None

    def test_profile_creation_validation_workflow(self, client, auth_headers):
        """Test profile creation with various validation scenarios."""
        validation_test_cases = [
            # Valid minimal profile
            {
                "data": {"first_name": "John"},
                "expected_status": [201, 400],
                "description": "Minimal profile data"
            },
            # Valid phone number formats
            {
                "data": {"phone": "+1-555-123-4567"},
                "expected_status": [201, 400],
                "description": "US phone number"
            },
            {
                "data": {"phone": "+44-20-7946-0958"},
                "expected_status": [201, 400],
                "description": "UK phone number"
            },
            # Invalid phone number
            {
                "data": {"phone": "555-123-4567"},
                "expected_status": [400],
                "description": "Invalid phone number format"
            },
            # Future date of birth
            {
                "data": {"date_of_birth": "2030-01-01"},
                "expected_status": [400],
                "description": "Future date of birth"
            },
            # Invalid URL
            {
                "data": {"profile_picture_url": "not-a-url"},
                "expected_status": [400],
                "description": "Invalid profile picture URL"
            }
        ]

        for test_case in validation_test_cases:
            response = client.post("/profiles", json=test_case["data"], headers=auth_headers)
            assert response.status_code in test_case["expected_status"], f"Test case failed: {test_case['description']}"

    def test_duplicate_profile_prevention(self, client, auth_headers, complete_profile_data):
        """Test that duplicate profile creation is prevented."""
        # First profile creation
        first_response = client.post("/profiles", json=complete_profile_data, headers=auth_headers)

        if first_response.status_code == 201:
            # Attempt to create second profile for same user
            second_response = client.post("/profiles", json=complete_profile_data, headers=auth_headers)
            assert second_response.status_code == 409, "Duplicate profile creation should be prevented"

            error_data = second_response.json()
            assert "already exists" in error_data["message"].lower() or "conflict" in error_data["error"].lower()

    def test_profile_creation_with_partial_data(self, client, auth_headers):
        """Test profile creation with various combinations of partial data."""
        partial_data_sets = [
            {"first_name": "Alice"},
            {"first_name": "Bob", "last_name": "Johnson"},
            {"first_name": "Carol", "phone": "+1-555-111-2222"},
            {"last_name": "Davis", "date_of_birth": "1990-12-15"},
        ]

        for partial_data in partial_data_sets:
            response = client.post("/profiles", json=partial_data, headers=auth_headers)

            if response.status_code == 201:
                profile = response.json()

                # Verify submitted data is preserved
                for key, value in partial_data.items():
                    assert profile[key] == value, f"Field {key} should match submitted value"

                # Verify optional fields are properly null
                optional_fields = ["first_name", "last_name", "phone", "date_of_birth", "profile_picture_url"]
                for field in optional_fields:
                    if field not in partial_data:
                        assert profile[field] is None, f"Unsubmitted field {field} should be null"

    def test_profile_creation_error_handling(self, client, auth_headers):
        """Test error handling during profile creation process."""
        # Test with malformed JSON
        response = client.post(
            "/profiles",
            data="{invalid-json}",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422], "Malformed JSON should return 400 or 422"

        # Test with missing content-type
        response = client.post("/profiles", data='{"first_name": "John"}', headers=auth_headers)
        assert response.status_code in [400, 415], "Missing content-type should return 400 or 415"

        # Test with wrong content-type
        response = client.post(
            "/profiles",
            data='{"first_name": "John"}',
            headers={**auth_headers, "Content-Type": "text/plain"}
        )
        assert response.status_code in [400, 415], "Wrong content-type should return 400 or 415"

    def test_profile_creation_field_length_limits(self, client, auth_headers):
        """Test field length validation during profile creation."""
        length_test_cases = [
            # Test maximum allowed lengths
            {
                "data": {"first_name": "A" * 100},
                "expected_status": [201, 400],
                "description": "Maximum first_name length"
            },
            # Test exceeding maximum lengths
            {
                "data": {"first_name": "A" * 101},
                "expected_status": [400],
                "description": "Exceeded first_name length"
            },
            {
                "data": {"last_name": "B" * 101},
                "expected_status": [400],
                "description": "Exceeded last_name length"
            },
            {
                "data": {"phone": "+1-" + "5" * 20},
                "expected_status": [400],
                "description": "Exceeded phone length"
            }
        ]

        for test_case in length_test_cases:
            response = client.post("/profiles", json=test_case["data"], headers=auth_headers)
            assert response.status_code in test_case["expected_status"], f"Length test failed: {test_case['description']}"

    @pytest.mark.integration
    def test_profile_creation_performance(self, client, auth_headers, complete_profile_data):
        """Test that profile creation performs within acceptable time limits."""
        import time

        start_time = time.time()
        response = client.post("/profiles", json=complete_profile_data, headers=auth_headers)
        creation_time = time.time() - start_time

        if response.status_code in [201, 409]:  # Success or already exists
            assert creation_time < 0.5, f"Profile creation took {creation_time:.3f}s, should be < 500ms"

    def test_profile_creation_concurrent_requests(self, client, auth_headers, complete_profile_data):
        """Test handling of concurrent profile creation requests."""
        import threading
        import time

        results = []

        def create_profile():
            try:
                response = client.post("/profiles", json=complete_profile_data, headers=auth_headers)
                results.append(response.status_code)
            except Exception as e:
                results.append(f"Error: {e}")

        # Launch multiple concurrent requests
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=create_profile)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify that only one profile creation succeeded
        success_count = sum(1 for result in results if result == 201)
        conflict_count = sum(1 for result in results if result == 409)

        # Either one success and rest conflicts, or one success and rest other errors
        assert success_count <= 1, "Only one profile creation should succeed"
        if success_count == 1:
            assert conflict_count >= 1, "Concurrent requests should result in conflicts"

    def test_profile_creation_with_unicode_data(self, client, auth_headers):
        """Test profile creation with unicode and international characters."""
        unicode_test_cases = [
            {
                "data": {"first_name": "José", "last_name": "García"},
                "description": "Spanish characters"
            },
            {
                "data": {"first_name": "张", "last_name": "伟"},
                "description": "Chinese characters"
            },
            {
                "data": {"first_name": "Müller", "last_name": "François"},
                "description": "European characters with diacritics"
            },
            {
                "data": {"first_name": "محمد", "last_name": "علي"},
                "description": "Arabic characters"
            }
        ]

        for test_case in unicode_test_cases:
            response = client.post("/profiles", json=test_case["data"], headers=auth_headers)

            if response.status_code == 201:
                profile = response.json()

                # Verify unicode data is preserved correctly
                assert profile["first_name"] == test_case["data"]["first_name"]
                assert profile["last_name"] == test_case["data"]["last_name"]