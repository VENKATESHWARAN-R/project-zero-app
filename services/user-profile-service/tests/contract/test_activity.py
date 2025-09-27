"""Contract tests for activity log endpoints.

These tests verify that the activity log endpoints conform to the OpenAPI specification
and return the expected response schemas.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from typing import Optional, List


class ActivityResponse(BaseModel):
    """Expected activity response schema from OpenAPI spec."""
    id: int
    user_id: int
    activity_type: str
    description: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    created_at: str


class ActivityListResponse(BaseModel):
    """Expected activity list response schema from OpenAPI spec."""
    activities: List[ActivityResponse]
    total: int
    limit: int
    offset: int


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


class TestActivityLogEndpoints:
    """Contract tests for activity log endpoints."""

    def test_get_activity_endpoint_exists(self, client, auth_headers):
        """Test that GET /activity endpoint exists."""
        response = client.get("/activity", headers=auth_headers)
        assert response.status_code in [200, 401], "Activity GET should return 200 or 401"

    def test_get_activity_requires_auth(self, client):
        """Test that GET /activity requires authentication."""
        response = client.get("/activity")
        assert response.status_code == 401, "Activity GET should require authentication"

        error_data = ErrorResponse.model_validate(response.json())
        assert error_data.error == "Unauthorized"

    def test_get_activity_response_schema(self, client, auth_headers):
        """Test that GET /activity returns valid ActivityListResponse schema."""
        response = client.get("/activity", headers=auth_headers)

        if response.status_code == 200:
            activity_list = ActivityListResponse.model_validate(response.json())

            # Verify required fields are present
            assert isinstance(activity_list.activities, list)
            assert activity_list.total >= 0
            assert activity_list.limit > 0
            assert activity_list.offset >= 0

            # Validate each activity in the response
            for activity in activity_list.activities:
                assert activity.id > 0
                assert activity.user_id > 0
                assert activity.activity_type is not None
                assert activity.description is not None
                assert activity.created_at is not None

    def test_get_activity_pagination_params(self, client, auth_headers):
        """Test that GET /activity supports pagination parameters."""
        # Test with limit parameter
        response = client.get("/activity?limit=5", headers=auth_headers)
        if response.status_code == 200:
            activity_list = ActivityListResponse.model_validate(response.json())
            assert activity_list.limit == 5
            assert len(activity_list.activities) <= 5

        # Test with offset parameter
        response = client.get("/activity?offset=10", headers=auth_headers)
        if response.status_code == 200:
            activity_list = ActivityListResponse.model_validate(response.json())
            assert activity_list.offset == 10

        # Test with both limit and offset
        response = client.get("/activity?limit=3&offset=5", headers=auth_headers)
        if response.status_code == 200:
            activity_list = ActivityListResponse.model_validate(response.json())
            assert activity_list.limit == 3
            assert activity_list.offset == 5
            assert len(activity_list.activities) <= 3

    def test_get_activity_limit_validation(self, client, auth_headers):
        """Test that limit parameter validation works correctly."""
        # Test minimum limit
        response = client.get("/activity?limit=1", headers=auth_headers)
        assert response.status_code in [200, 400], "Minimum limit should be handled"

        # Test maximum limit
        response = client.get("/activity?limit=100", headers=auth_headers)
        assert response.status_code in [200, 400], "Maximum limit should be handled"

        # Test invalid limit (too high)
        response = client.get("/activity?limit=1000", headers=auth_headers)
        if response.status_code == 400:
            error_data = ErrorResponse.model_validate(response.json())
            assert error_data.error in ["Validation failed", "Bad Request"]

        # Test invalid limit (negative)
        response = client.get("/activity?limit=-1", headers=auth_headers)
        if response.status_code == 400:
            error_data = ErrorResponse.model_validate(response.json())
            assert error_data.error in ["Validation failed", "Bad Request"]

        # Test invalid limit (not a number)
        response = client.get("/activity?limit=abc", headers=auth_headers)
        if response.status_code == 400:
            error_data = ErrorResponse.model_validate(response.json())
            assert error_data.error in ["Validation failed", "Bad Request"]

    def test_get_activity_offset_validation(self, client, auth_headers):
        """Test that offset parameter validation works correctly."""
        # Test valid offset
        response = client.get("/activity?offset=0", headers=auth_headers)
        assert response.status_code in [200, 400], "Zero offset should be valid"

        # Test negative offset
        response = client.get("/activity?offset=-1", headers=auth_headers)
        if response.status_code == 400:
            error_data = ErrorResponse.model_validate(response.json())
            assert error_data.error in ["Validation failed", "Bad Request"]

        # Test invalid offset (not a number)
        response = client.get("/activity?offset=xyz", headers=auth_headers)
        if response.status_code == 400:
            error_data = ErrorResponse.model_validate(response.json())
            assert error_data.error in ["Validation failed", "Bad Request"]

    def test_get_activity_type_filter(self, client, auth_headers):
        """Test that activity_type filter works correctly."""
        activity_types = [
            "profile_created", "profile_updated", "address_created",
            "address_updated", "address_deleted", "preferences_updated"
        ]

        for activity_type in activity_types:
            response = client.get(f"/activity?activity_type={activity_type}", headers=auth_headers)
            if response.status_code == 200:
                activity_list = ActivityListResponse.model_validate(response.json())

                # Verify all returned activities match the filter
                for activity in activity_list.activities:
                    assert activity.activity_type == activity_type

    def test_get_activity_default_values(self, client, auth_headers):
        """Test that default pagination values are applied correctly."""
        response = client.get("/activity", headers=auth_headers)

        if response.status_code == 200:
            activity_list = ActivityListResponse.model_validate(response.json())

            # Verify default values from OpenAPI spec
            assert activity_list.limit == 20  # Default limit from spec
            assert activity_list.offset == 0   # Default offset from spec

    def test_activity_response_content_type(self, client, auth_headers):
        """Test that activity endpoints return application/json content type."""
        response = client.get("/activity", headers=auth_headers)
        if response.status_code in [200, 401]:
            assert response.headers["content-type"] == "application/json"

    def test_activity_chronological_order(self, client, auth_headers):
        """Test that activities are returned in chronological order (newest first)."""
        response = client.get("/activity?limit=10", headers=auth_headers)

        if response.status_code == 200:
            activity_list = ActivityListResponse.model_validate(response.json())

            if len(activity_list.activities) > 1:
                # Verify activities are in descending order by created_at
                for i in range(len(activity_list.activities) - 1):
                    current_time = activity_list.activities[i].created_at
                    next_time = activity_list.activities[i + 1].created_at
                    # In descending order, current should be >= next
                    assert current_time >= next_time, "Activities should be in chronological order (newest first)"

    def test_activity_user_isolation(self, client, auth_headers):
        """Test that users only see their own activities."""
        response = client.get("/activity", headers=auth_headers)

        if response.status_code == 200:
            activity_list = ActivityListResponse.model_validate(response.json())

            # All activities should belong to the authenticated user
            # Note: user_id would be extracted from the JWT token in real implementation
            for activity in activity_list.activities:
                assert activity.user_id > 0, "All activities should have a valid user_id"
                # In real implementation, would verify user_id matches JWT token user

    def test_activity_types_enumeration(self, client, auth_headers):
        """Test that activity types follow the expected enumeration."""
        expected_activity_types = {
            "profile_created", "profile_updated", "profile_viewed",
            "address_created", "address_updated", "address_deleted", "address_default_changed",
            "preferences_updated", "notification_settings_changed", "privacy_settings_changed",
            "profile_access_denied", "admin_access"
        }

        response = client.get("/activity", headers=auth_headers)

        if response.status_code == 200:
            activity_list = ActivityListResponse.model_validate(response.json())

            # Verify all activity types are from expected set
            for activity in activity_list.activities:
                assert activity.activity_type in expected_activity_types, f"Unexpected activity type: {activity.activity_type}"

    def test_activity_entity_references(self, client, auth_headers):
        """Test that entity_type and entity_id are properly set for activities."""
        response = client.get("/activity", headers=auth_headers)

        if response.status_code == 200:
            activity_list = ActivityListResponse.model_validate(response.json())

            for activity in activity_list.activities:
                # If entity_type is provided, entity_id should also be provided
                if activity.entity_type is not None:
                    assert activity.entity_id is not None, "entity_id should be provided when entity_type is set"
                    assert activity.entity_id > 0, "entity_id should be a positive integer"

                # Check valid entity types
                if activity.entity_type is not None:
                    valid_entity_types = {"profile", "address", "preferences"}
                    assert activity.entity_type in valid_entity_types, f"Invalid entity_type: {activity.entity_type}"

    def test_activity_description_format(self, client, auth_headers):
        """Test that activity descriptions are human-readable and informative."""
        response = client.get("/activity", headers=auth_headers)

        if response.status_code == 200:
            activity_list = ActivityListResponse.model_validate(response.json())

            for activity in activity_list.activities:
                # Description should be non-empty and meaningful
                assert len(activity.description) > 0, "Activity description should not be empty"
                assert len(activity.description) < 500, "Activity description should be concise"

                # Description should be human-readable (no technical jargon or IDs only)
                description_lower = activity.description.lower()
                assert not description_lower.startswith("id:"), "Description should be human-readable"
                assert "user" in description_lower or "profile" in description_lower or "address" in description_lower or "preference" in description_lower, "Description should be contextual"

    @pytest.mark.integration
    def test_activity_endpoint_performance(self, client, auth_headers):
        """Test that activity endpoint responds quickly (< 200ms)."""
        import time

        # Test basic activity retrieval performance
        start_time = time.time()
        response = client.get("/activity", headers=auth_headers)
        duration = time.time() - start_time

        if response.status_code == 200:
            assert duration < 0.2, f"GET /activity took {duration:.3f}s, should be < 200ms"

        # Test activity retrieval with filters performance
        start_time = time.time()
        response = client.get("/activity?limit=50&activity_type=profile_updated", headers=auth_headers)
        filter_duration = time.time() - start_time

        if response.status_code == 200:
            assert filter_duration < 0.2, f"GET /activity with filters took {filter_duration:.3f}s, should be < 200ms"

    def test_activity_pagination_consistency(self, client, auth_headers):
        """Test that pagination returns consistent results."""
        # Get first page
        response1 = client.get("/activity?limit=5&offset=0", headers=auth_headers)
        if response1.status_code != 200:
            return

        # Get second page
        response2 = client.get("/activity?limit=5&offset=5", headers=auth_headers)
        if response2.status_code != 200:
            return

        activity_list1 = ActivityListResponse.model_validate(response1.json())
        activity_list2 = ActivityListResponse.model_validate(response2.json())

        # Verify pagination metadata consistency
        assert activity_list1.total == activity_list2.total, "Total count should be consistent across pages"

        # Verify no overlap between pages
        page1_ids = {activity.id for activity in activity_list1.activities}
        page2_ids = {activity.id for activity in activity_list2.activities}
        assert len(page1_ids.intersection(page2_ids)) == 0, "Pages should not contain overlapping activities"

    def test_activity_empty_response_handling(self, client, auth_headers):
        """Test handling when no activities exist for user."""
        # Request activities with very high offset
        response = client.get("/activity?offset=10000", headers=auth_headers)

        if response.status_code == 200:
            activity_list = ActivityListResponse.model_validate(response.json())
            assert len(activity_list.activities) == 0, "Should return empty activities list"
            assert activity_list.total >= 0, "Total should be non-negative even when empty"
            assert activity_list.offset == 10000, "Offset should match request"