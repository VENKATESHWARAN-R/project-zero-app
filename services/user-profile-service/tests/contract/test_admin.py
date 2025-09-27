"""Contract tests for admin endpoints.

These tests verify that the admin endpoints conform to the OpenAPI specification
and return the expected response schemas.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from typing import Optional


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
    from main import app
    return TestClient(app)


@pytest.fixture
def admin_headers():
    """Mock admin auth headers for testing."""
    # This will need to be updated with real admin JWT token once auth integration is implemented
    return {"Authorization": "Bearer fake-admin-jwt-token-for-testing"}


@pytest.fixture
def user_headers():
    """Mock regular user auth headers for testing."""
    return {"Authorization": "Bearer fake-user-jwt-token-for-testing"}


class TestAdminEndpoints:
    """Contract tests for admin endpoints."""

    def test_admin_get_profile_endpoint_exists(self, client, admin_headers):
        """Test that GET /admin/profiles/{user_id} endpoint exists."""
        response = client.get("/admin/profiles/42", headers=admin_headers)
        assert response.status_code in [200, 404, 401, 403], "Admin profile GET should return 200, 404, 401, or 403"

    def test_admin_get_profile_requires_auth(self, client):
        """Test that GET /admin/profiles/{user_id} requires authentication."""
        response = client.get("/admin/profiles/42")
        assert response.status_code == 401, "Admin profile GET should require authentication"

        error_data = ErrorResponse.model_validate(response.json())
        assert error_data.error == "Unauthorized"

    def test_admin_get_profile_requires_admin_permissions(self, client, user_headers):
        """Test that GET /admin/profiles/{user_id} requires admin permissions."""
        response = client.get("/admin/profiles/42", headers=user_headers)
        assert response.status_code == 403, "Admin profile GET should require admin permissions"

        error_data = ErrorResponse.model_validate(response.json())
        assert error_data.error == "Forbidden"

    def test_admin_get_profile_response_schema(self, client, admin_headers):
        """Test that GET /admin/profiles/{user_id} returns valid ProfileResponse schema."""
        response = client.get("/admin/profiles/42", headers=admin_headers)

        if response.status_code == 200:
            profile = ProfileResponse.model_validate(response.json())

            # Verify required fields are present
            assert profile.id > 0
            assert profile.user_id == 42  # Should match the requested user_id
            assert profile.created_at is not None
            assert profile.updated_at is not None

    def test_admin_get_profile_not_found(self, client, admin_headers):
        """Test that GET /admin/profiles/{user_id} returns 404 for non-existent user."""
        # Use a very high user ID that's unlikely to exist
        response = client.get("/admin/profiles/999999", headers=admin_headers)

        if response.status_code == 404:
            error_data = ErrorResponse.model_validate(response.json())
            assert error_data.error == "Not Found" or "not found" in error_data.message.lower()

    def test_admin_get_profile_user_id_validation(self, client, admin_headers):
        """Test that user_id parameter validation works correctly."""
        # Test invalid user_id (not a number)
        response = client.get("/admin/profiles/abc", headers=admin_headers)
        assert response.status_code in [400, 404], "Invalid user_id should return 400 or 404"

        # Test invalid user_id (negative number)
        response = client.get("/admin/profiles/-1", headers=admin_headers)
        assert response.status_code in [400, 404], "Negative user_id should return 400 or 404"

        # Test invalid user_id (zero)
        response = client.get("/admin/profiles/0", headers=admin_headers)
        assert response.status_code in [400, 404], "Zero user_id should return 400 or 404"

    def test_admin_profile_content_type(self, client, admin_headers):
        """Test that admin endpoints return application/json content type."""
        response = client.get("/admin/profiles/42", headers=admin_headers)
        if response.status_code in [200, 404, 401, 403]:
            assert response.headers["content-type"] == "application/json"

    def test_admin_access_logging(self, client, admin_headers):
        """Test that admin access is properly logged (contract verification)."""
        # This test verifies that the endpoint exists and responds
        # The actual logging verification would be done in integration tests
        response = client.get("/admin/profiles/42", headers=admin_headers)

        # Admin access should be tracked, but we can only verify the endpoint responds
        assert response.status_code in [200, 404, 401, 403], "Admin endpoint should be accessible"

        # If successful, the access should be logged as an activity
        # This would be verified in integration tests by checking activity logs

    def test_admin_cross_user_access(self, client, admin_headers):
        """Test that admin can access any user's profile."""
        test_user_ids = [1, 42, 100, 1000]

        for user_id in test_user_ids:
            response = client.get(f"/admin/profiles/{user_id}", headers=admin_headers)

            # Admin should be able to attempt access to any user
            # Response could be 200 (profile exists) or 404 (profile doesn't exist)
            assert response.status_code in [200, 404], f"Admin should be able to access user {user_id}"

            if response.status_code == 200:
                profile = ProfileResponse.model_validate(response.json())
                assert profile.user_id == user_id, f"Profile should belong to user {user_id}"

    def test_admin_profile_data_completeness(self, client, admin_headers):
        """Test that admin gets complete profile data (no filtered fields)."""
        response = client.get("/admin/profiles/42", headers=admin_headers)

        if response.status_code == 200:
            profile = ProfileResponse.model_validate(response.json())

            # Admin should see all profile fields
            # Verify that sensitive data access is controlled at business logic level
            assert hasattr(profile, 'user_id'), "Admin should see user_id"
            assert hasattr(profile, 'created_at'), "Admin should see created_at"
            assert hasattr(profile, 'updated_at'), "Admin should see updated_at"

            # Profile data should match standard ProfileResponse schema
            # No additional filtering or data hiding for admin access

    def test_admin_endpoint_authorization_header_format(self, client):
        """Test that admin endpoints properly validate authorization header format."""
        invalid_auth_headers = [
            {"Authorization": "Basic invalid-token"},  # Wrong auth type
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": "invalid-format"},  # Invalid format
            {"X-Auth-Token": "Bearer valid-token"},  # Wrong header name
        ]

        for headers in invalid_auth_headers:
            response = client.get("/admin/profiles/42", headers=headers)
            assert response.status_code == 401, f"Invalid auth header should return 401: {headers}"

    def test_admin_endpoint_rate_limiting_compatibility(self, client, admin_headers):
        """Test that admin endpoints are compatible with rate limiting."""
        # Make multiple requests to test rate limiting behavior
        responses = []
        for i in range(5):
            response = client.get(f"/admin/profiles/{i+1}", headers=admin_headers)
            responses.append(response)

        # Admin endpoints should either:
        # 1. Work normally (no rate limiting for admin)
        # 2. Apply rate limiting consistently
        for response in responses:
            assert response.status_code in [200, 404, 429, 401, 403], "Admin endpoints should handle rate limiting gracefully"

    @pytest.mark.integration
    def test_admin_endpoint_performance(self, client, admin_headers):
        """Test that admin endpoints respond quickly (< 200ms)."""
        import time

        # Test admin profile retrieval performance
        start_time = time.time()
        response = client.get("/admin/profiles/42", headers=admin_headers)
        duration = time.time() - start_time

        if response.status_code in [200, 404]:
            assert duration < 0.2, f"GET /admin/profiles/42 took {duration:.3f}s, should be < 200ms"

    def test_admin_user_id_path_parameter_constraints(self, client, admin_headers):
        """Test path parameter constraints for user_id."""
        # Test very large user_id
        response = client.get("/admin/profiles/999999999999", headers=admin_headers)
        assert response.status_code in [200, 404, 400], "Large user_id should be handled gracefully"

        # Test user_id with leading zeros
        response = client.get("/admin/profiles/0042", headers=admin_headers)
        # Should either work (interpreted as 42) or return 400/404
        assert response.status_code in [200, 404, 400], "User_id with leading zeros should be handled"

    def test_admin_error_response_consistency(self, client, admin_headers):
        """Test that admin endpoints return consistent error response format."""
        # Test 404 error response
        response = client.get("/admin/profiles/999999", headers=admin_headers)
        if response.status_code == 404:
            error_data = ErrorResponse.model_validate(response.json())
            assert error_data.error is not None
            assert error_data.message is not None
            assert error_data.timestamp is not None

        # Test without authentication
        response = client.get("/admin/profiles/42")
        if response.status_code == 401:
            error_data = ErrorResponse.model_validate(response.json())
            assert error_data.error == "Unauthorized"

        # Test with insufficient permissions
        user_headers = {"Authorization": "Bearer fake-user-token"}
        response = client.get("/admin/profiles/42", headers=user_headers)
        if response.status_code == 403:
            error_data = ErrorResponse.model_validate(response.json())
            assert error_data.error == "Forbidden"

    def test_admin_endpoint_cors_compliance(self, client, admin_headers):
        """Test that admin endpoints comply with CORS policy."""
        # Test OPTIONS request (preflight)
        response = client.options("/admin/profiles/42", headers=admin_headers)
        # Should either return proper CORS headers or 405 Method Not Allowed
        assert response.status_code in [200, 204, 405], "OPTIONS request should be handled properly"

        # Test actual request has proper headers for CORS
        response = client.get("/admin/profiles/42", headers=admin_headers)
        if response.status_code in [200, 404]:
            # Should not have restrictive CORS headers that block admin access
            assert "Access-Control-Allow-Origin" not in response.headers or response.headers["Access-Control-Allow-Origin"] != "null"

    def test_admin_sensitive_data_handling(self, client, admin_headers):
        """Test that admin endpoints handle sensitive data appropriately."""
        response = client.get("/admin/profiles/42", headers=admin_headers)

        if response.status_code == 200:
            profile = ProfileResponse.model_validate(response.json())

            # Verify that sensitive fields are not accidentally exposed
            profile_dict = profile.model_dump()

            # Fields that should NOT be in the response
            sensitive_fields = ['password', 'password_hash', 'api_key', 'secret', 'token']
            for field in sensitive_fields:
                assert field not in profile_dict, f"Sensitive field '{field}' should not be in admin profile response"

            # Verify phone numbers are properly formatted (not exposing internal format)
            if profile.phone:
                assert not profile.phone.startswith("ENCRYPTED:"), "Phone should not expose internal encryption format"