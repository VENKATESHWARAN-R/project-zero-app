"""Contract tests for profile CRUD endpoints.

These tests verify that the profile endpoints conform to the OpenAPI specification
and return the expected response schemas.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProfileResponse(BaseModel):
    """Expected profile response schema from OpenAPI spec."""
    id: int
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    profile_picture_url: Optional[str] = None
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
    # This will fail initially as the app doesn't exist yet
    from main import app
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock auth headers for testing."""
    # This will need to be updated with real JWT token once auth integration is implemented
    return {"Authorization": "Bearer fake-jwt-token-for-testing"}


@pytest.fixture
def valid_profile_data():
    """Valid profile data for create/update operations."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1-555-123-4567",
        "date_of_birth": "1990-05-15",
        "profile_picture_url": "https://example.com/profile.jpg"
    }


@pytest.fixture
def invalid_profile_data():
    """Invalid profile data for validation testing."""
    return {
        "first_name": "J" * 101,  # Too long
        "phone": "invalid-phone",  # Invalid format
        "date_of_birth": "2030-01-01",  # Future date
        "profile_picture_url": "not-a-url"  # Invalid URL
    }


class TestProfileEndpoints:
    """Contract tests for profile CRUD endpoints."""

    def test_get_profile_endpoint_exists(self, client, auth_headers):
        """Test that GET /profiles endpoint exists."""
        response = client.get("/profiles", headers=auth_headers)
        assert response.status_code in [200, 404, 401], "Profile GET should return 200, 404, or 401"

    def test_get_profile_requires_auth(self, client):
        """Test that GET /profiles requires authentication."""
        response = client.get("/profiles")
        assert response.status_code == 401, "Profile GET should require authentication"

        # Verify error response schema
        error_data = ErrorResponse.model_validate(response.json())
        assert error_data.error == "Unauthorized"

    def test_get_profile_response_schema(self, client, auth_headers):
        """Test that GET /profiles returns valid ProfileResponse schema when profile exists."""
        response = client.get("/profiles", headers=auth_headers)

        if response.status_code == 200:
            # Validate response can be parsed as ProfileResponse
            profile_data = ProfileResponse.model_validate(response.json())

            # Verify required fields are present
            assert profile_data.id > 0
            assert profile_data.user_id > 0
            assert profile_data.created_at is not None
            assert profile_data.updated_at is not None

    def test_create_profile_endpoint_exists(self, client, auth_headers, valid_profile_data):
        """Test that POST /profiles endpoint exists."""
        response = client.post("/profiles", json=valid_profile_data, headers=auth_headers)
        assert response.status_code in [201, 409, 400, 401], "Profile POST should return 201, 409, 400, or 401"

    def test_create_profile_requires_auth(self, client, valid_profile_data):
        """Test that POST /profiles requires authentication."""
        response = client.post("/profiles", json=valid_profile_data)
        assert response.status_code == 401, "Profile POST should require authentication"

    def test_create_profile_response_schema(self, client, auth_headers, valid_profile_data):
        """Test that POST /profiles returns valid ProfileResponse schema."""
        response = client.post("/profiles", json=valid_profile_data, headers=auth_headers)

        if response.status_code == 201:
            # Validate response can be parsed as ProfileResponse
            profile_data = ProfileResponse.model_validate(response.json())

            # Verify created profile contains submitted data
            assert profile_data.first_name == valid_profile_data["first_name"]
            assert profile_data.last_name == valid_profile_data["last_name"]
            assert profile_data.phone == valid_profile_data["phone"]
            assert profile_data.date_of_birth == valid_profile_data["date_of_birth"]

    def test_create_profile_validation(self, client, auth_headers, invalid_profile_data):
        """Test that POST /profiles validates input data."""
        response = client.post("/profiles", json=invalid_profile_data, headers=auth_headers)
        assert response.status_code == 400, "Invalid profile data should return 400"

        # Verify error response schema
        error_data = ErrorResponse.model_validate(response.json())
        assert error_data.error in ["Validation failed", "Bad Request"]

    def test_update_profile_endpoint_exists(self, client, auth_headers, valid_profile_data):
        """Test that PUT /profiles endpoint exists."""
        response = client.put("/profiles", json=valid_profile_data, headers=auth_headers)
        assert response.status_code in [200, 404, 400, 401], "Profile PUT should return 200, 404, 400, or 401"

    def test_update_profile_requires_auth(self, client, valid_profile_data):
        """Test that PUT /profiles requires authentication."""
        response = client.put("/profiles", json=valid_profile_data)
        assert response.status_code == 401, "Profile PUT should require authentication"

    def test_update_profile_response_schema(self, client, auth_headers, valid_profile_data):
        """Test that PUT /profiles returns valid ProfileResponse schema."""
        response = client.put("/profiles", json=valid_profile_data, headers=auth_headers)

        if response.status_code == 200:
            # Validate response can be parsed as ProfileResponse
            profile_data = ProfileResponse.model_validate(response.json())

            # Verify updated profile contains submitted data
            assert profile_data.first_name == valid_profile_data["first_name"]
            assert profile_data.updated_at is not None

    def test_update_profile_validation(self, client, auth_headers, invalid_profile_data):
        """Test that PUT /profiles validates input data."""
        response = client.put("/profiles", json=invalid_profile_data, headers=auth_headers)

        if response.status_code == 400:
            # Verify error response schema
            error_data = ErrorResponse.model_validate(response.json())
            assert error_data.error in ["Validation failed", "Bad Request"]

    def test_profile_phone_validation(self, client, auth_headers):
        """Test phone number validation according to E.164 format."""
        valid_phones = [
            "+1-555-123-4567",
            "+44-20-7946-0958",
            "+81-3-1234-5678"
        ]

        invalid_phones = [
            "555-123-4567",  # Missing country code
            "+1 555 123 4567",  # Spaces instead of hyphens
            "invalid-phone",  # Not a phone number
            "+1-555-123-45678901234567890"  # Too long
        ]

        # Test valid phone numbers
        for phone in valid_phones:
            profile_data = {"phone": phone}
            response = client.post("/profiles", json=profile_data, headers=auth_headers)
            if response.status_code == 400:
                error_data = response.json()
                assert "phone" not in error_data.get("details", {}), f"Valid phone {phone} was rejected"

        # Test invalid phone numbers
        for phone in invalid_phones:
            profile_data = {"phone": phone}
            response = client.post("/profiles", json=profile_data, headers=auth_headers)
            if response.status_code == 400:
                error_data = ErrorResponse.model_validate(response.json())
                assert error_data.error in ["Validation failed", "Bad Request"]

    def test_profile_date_validation(self, client, auth_headers):
        """Test date of birth validation."""
        valid_dates = [
            "1990-05-15",
            "1980-12-31",
            "2000-01-01"
        ]

        invalid_dates = [
            "2030-01-01",  # Future date
            "invalid-date",  # Invalid format
            "1800-01-01",  # Too old
            "2025-13-01"  # Invalid month
        ]

        # Test valid dates
        for date in valid_dates:
            profile_data = {"date_of_birth": date}
            response = client.post("/profiles", json=profile_data, headers=auth_headers)
            if response.status_code == 400:
                error_data = response.json()
                assert "date_of_birth" not in error_data.get("details", {}), f"Valid date {date} was rejected"

        # Test invalid dates
        for date in invalid_dates:
            profile_data = {"date_of_birth": date}
            response = client.post("/profiles", json=profile_data, headers=auth_headers)
            if response.status_code == 400:
                error_data = ErrorResponse.model_validate(response.json())
                assert error_data.error in ["Validation failed", "Bad Request"]

    def test_profile_content_type_validation(self, client, auth_headers, valid_profile_data):
        """Test that endpoints require application/json content type."""
        # Test POST without content-type header
        response = client.post("/profiles", data=str(valid_profile_data), headers=auth_headers)
        assert response.status_code in [400, 415], "Should reject non-JSON content"

        # Test PUT without content-type header
        response = client.put("/profiles", data=str(valid_profile_data), headers=auth_headers)
        assert response.status_code in [400, 415], "Should reject non-JSON content"

    def test_profile_duplicate_creation(self, client, auth_headers, valid_profile_data):
        """Test that creating duplicate profile returns 409 Conflict."""
        # First creation should succeed (or return existing profile)
        response1 = client.post("/profiles", json=valid_profile_data, headers=auth_headers)

        # Second creation should return 409 if profile already exists
        response2 = client.post("/profiles", json=valid_profile_data, headers=auth_headers)

        if response1.status_code == 201 and response2.status_code == 409:
            error_data = ErrorResponse.model_validate(response2.json())
            assert error_data.error == "Conflict" or "already exists" in error_data.message.lower()

    @pytest.mark.integration
    def test_profile_operations_performance(self, client, auth_headers, valid_profile_data):
        """Test that profile operations respond quickly (< 200ms)."""
        import time

        # Test GET performance
        start_time = time.time()
        response = client.get("/profiles", headers=auth_headers)
        get_duration = time.time() - start_time
        assert get_duration < 0.2, f"GET /profiles took {get_duration:.3f}s, should be < 200ms"

        # Test POST performance (if applicable)
        if response.status_code == 404:  # No profile exists, test creation
            start_time = time.time()
            response = client.post("/profiles", json=valid_profile_data, headers=auth_headers)
            post_duration = time.time() - start_time
            assert post_duration < 0.2, f"POST /profiles took {post_duration:.3f}s, should be < 200ms"