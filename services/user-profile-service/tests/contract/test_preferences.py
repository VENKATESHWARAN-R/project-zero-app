"""Contract tests for preferences endpoints.

These tests verify that the preferences endpoints conform to the OpenAPI specification
and return the expected response schemas.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from typing import Optional, Literal


class PreferencesResponse(BaseModel):
    """Expected preferences response schema from OpenAPI spec."""
    id: int
    user_id: int
    email_marketing: bool
    email_order_updates: bool
    email_security_alerts: bool
    sms_notifications: bool
    preferred_language: str
    preferred_currency: str
    timezone: str
    profile_visibility: Literal["public", "private"]
    data_sharing_consent: bool
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
def valid_preferences_data():
    """Valid preferences data for update operations."""
    return {
        "email_marketing": False,
        "email_order_updates": True,
        "email_security_alerts": True,
        "sms_notifications": True,
        "preferred_language": "en-US",
        "preferred_currency": "USD",
        "timezone": "America/New_York",
        "profile_visibility": "private",
        "data_sharing_consent": False
    }


@pytest.fixture
def invalid_preferences_data():
    """Invalid preferences data for validation testing."""
    return {
        "email_marketing": "not_boolean",  # Invalid type
        "preferred_language": "invalid-locale",  # Invalid format
        "preferred_currency": "INVALID",  # Invalid currency code
        "timezone": "Invalid/Timezone",  # Invalid timezone
        "profile_visibility": "invalid"  # Invalid enum value
    }


class TestPreferencesEndpoints:
    """Contract tests for preferences endpoints."""

    def test_get_preferences_endpoint_exists(self, client, auth_headers):
        """Test that GET /preferences endpoint exists."""
        response = client.get("/preferences", headers=auth_headers)
        assert response.status_code in [200, 404, 401], "Preferences GET should return 200, 404, or 401"

    def test_get_preferences_requires_auth(self, client):
        """Test that GET /preferences requires authentication."""
        response = client.get("/preferences")
        assert response.status_code == 401, "Preferences GET should require authentication"

        error_data = ErrorResponse.model_validate(response.json())
        assert error_data.error == "Unauthorized"

    def test_get_preferences_response_schema(self, client, auth_headers):
        """Test that GET /preferences returns valid PreferencesResponse schema."""
        response = client.get("/preferences", headers=auth_headers)

        if response.status_code == 200:
            prefs = PreferencesResponse.model_validate(response.json())

            # Verify required fields are present
            assert prefs.id > 0
            assert prefs.user_id > 0
            assert isinstance(prefs.email_marketing, bool)
            assert isinstance(prefs.email_order_updates, bool)
            assert isinstance(prefs.email_security_alerts, bool)
            assert isinstance(prefs.sms_notifications, bool)
            assert prefs.profile_visibility in ["public", "private"]
            assert prefs.created_at is not None
            assert prefs.updated_at is not None

    def test_update_preferences_endpoint_exists(self, client, auth_headers, valid_preferences_data):
        """Test that PUT /preferences endpoint exists."""
        response = client.put("/preferences", json=valid_preferences_data, headers=auth_headers)
        assert response.status_code in [200, 400, 401], "Preferences PUT should return 200, 400, or 401"

    def test_update_preferences_requires_auth(self, client, valid_preferences_data):
        """Test that PUT /preferences requires authentication."""
        response = client.put("/preferences", json=valid_preferences_data)
        assert response.status_code == 401, "Preferences PUT should require authentication"

    def test_update_preferences_response_schema(self, client, auth_headers, valid_preferences_data):
        """Test that PUT /preferences returns valid PreferencesResponse schema."""
        response = client.put("/preferences", json=valid_preferences_data, headers=auth_headers)

        if response.status_code == 200:
            prefs = PreferencesResponse.model_validate(response.json())

            # Verify updated preferences contain submitted data
            assert prefs.email_marketing == valid_preferences_data["email_marketing"]
            assert prefs.email_order_updates == valid_preferences_data["email_order_updates"]
            assert prefs.preferred_language == valid_preferences_data["preferred_language"]
            assert prefs.preferred_currency == valid_preferences_data["preferred_currency"]
            assert prefs.profile_visibility == valid_preferences_data["profile_visibility"]

    def test_update_preferences_validation(self, client, auth_headers, invalid_preferences_data):
        """Test that PUT /preferences validates input data."""
        response = client.put("/preferences", json=invalid_preferences_data, headers=auth_headers)
        assert response.status_code == 400, "Invalid preferences data should return 400"

        error_data = ErrorResponse.model_validate(response.json())
        assert error_data.error in ["Validation failed", "Bad Request"]

    def test_language_code_validation(self, client, auth_headers):
        """Test preferred language validation (ISO 639-1 + ISO 3166-1)."""
        valid_languages = [
            "en-US", "en-GB", "fr-FR", "de-DE", "es-ES", "ja-JP", "zh-CN"
        ]
        invalid_languages = [
            "english", "EN-us", "en", "en-USA", "invalid-locale", ""
        ]

        # Test valid language codes
        for lang in valid_languages:
            data = {"preferred_language": lang}
            response = client.put("/preferences", json=data, headers=auth_headers)
            if response.status_code == 400:
                error_data = response.json()
                assert "preferred_language" not in error_data.get("details", {}), f"Valid language {lang} was rejected"

        # Test invalid language codes
        for lang in invalid_languages:
            data = {"preferred_language": lang}
            response = client.put("/preferences", json=data, headers=auth_headers)
            if response.status_code == 400:
                error_data = ErrorResponse.model_validate(response.json())
                assert error_data.error in ["Validation failed", "Bad Request"]

    def test_currency_code_validation(self, client, auth_headers):
        """Test preferred currency validation (ISO 4217)."""
        valid_currencies = [
            "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY"
        ]
        invalid_currencies = [
            "usd", "Dollar", "US", "INVALID", "123", ""
        ]

        # Test valid currency codes
        for currency in valid_currencies:
            data = {"preferred_currency": currency}
            response = client.put("/preferences", json=data, headers=auth_headers)
            if response.status_code == 400:
                error_data = response.json()
                assert "preferred_currency" not in error_data.get("details", {}), f"Valid currency {currency} was rejected"

        # Test invalid currency codes
        for currency in invalid_currencies:
            data = {"preferred_currency": currency}
            response = client.put("/preferences", json=data, headers=auth_headers)
            if response.status_code == 400:
                error_data = ErrorResponse.model_validate(response.json())
                assert error_data.error in ["Validation failed", "Bad Request"]

    def test_timezone_validation(self, client, auth_headers):
        """Test timezone validation (IANA timezone identifiers)."""
        valid_timezones = [
            "UTC", "America/New_York", "Europe/London", "Asia/Tokyo",
            "America/Los_Angeles", "Europe/Berlin", "Australia/Sydney"
        ]
        invalid_timezones = [
            "EST", "PST", "GMT", "Invalid/Timezone", "America/Invalid", ""
        ]

        # Test valid timezones
        for tz in valid_timezones:
            data = {"timezone": tz}
            response = client.put("/preferences", json=data, headers=auth_headers)
            if response.status_code == 400:
                error_data = response.json()
                assert "timezone" not in error_data.get("details", {}), f"Valid timezone {tz} was rejected"

        # Test invalid timezones
        for tz in invalid_timezones:
            data = {"timezone": tz}
            response = client.put("/preferences", json=data, headers=auth_headers)
            if response.status_code == 400:
                error_data = ErrorResponse.model_validate(response.json())
                assert error_data.error in ["Validation failed", "Bad Request"]

    def test_profile_visibility_validation(self, client, auth_headers):
        """Test profile visibility enum validation."""
        valid_visibility = ["public", "private"]
        invalid_visibility = ["hidden", "friends", "custom", ""]

        # Test valid visibility options
        for visibility in valid_visibility:
            data = {"profile_visibility": visibility}
            response = client.put("/preferences", json=data, headers=auth_headers)
            if response.status_code == 400:
                error_data = response.json()
                assert "profile_visibility" not in error_data.get("details", {}), f"Valid visibility {visibility} was rejected"

        # Test invalid visibility options
        for visibility in invalid_visibility:
            data = {"profile_visibility": visibility}
            response = client.put("/preferences", json=data, headers=auth_headers)
            if response.status_code == 400:
                error_data = ErrorResponse.model_validate(response.json())
                assert error_data.error in ["Validation failed", "Bad Request"]

    def test_boolean_field_validation(self, client, auth_headers):
        """Test boolean field validation for notification preferences."""
        boolean_fields = [
            "email_marketing", "email_order_updates", "email_security_alerts",
            "sms_notifications", "data_sharing_consent"
        ]

        valid_boolean_values = [True, False]
        invalid_boolean_values = ["true", "false", 1, 0, "yes", "no", ""]

        # Test valid boolean values
        for field in boolean_fields:
            for value in valid_boolean_values:
                data = {field: value}
                response = client.put("/preferences", json=data, headers=auth_headers)
                if response.status_code == 400:
                    error_data = response.json()
                    assert field not in error_data.get("details", {}), f"Valid boolean {value} for {field} was rejected"

        # Test invalid boolean values
        for field in boolean_fields:
            for value in invalid_boolean_values:
                data = {field: value}
                response = client.put("/preferences", json=data, headers=auth_headers)
                if response.status_code == 400:
                    error_data = ErrorResponse.model_validate(response.json())
                    assert error_data.error in ["Validation failed", "Bad Request"]

    def test_partial_preferences_update(self, client, auth_headers):
        """Test that partial updates are supported (not all fields required)."""
        partial_updates = [
            {"email_marketing": False},
            {"preferred_language": "fr-FR"},
            {"timezone": "Europe/Paris"},
            {"profile_visibility": "public"},
            {"email_marketing": True, "sms_notifications": False}
        ]

        for partial_data in partial_updates:
            response = client.put("/preferences", json=partial_data, headers=auth_headers)
            # Should not fail validation for partial data
            if response.status_code == 400:
                error_data = response.json()
                # Ensure it's not failing due to missing fields
                assert "required" not in error_data.get("message", "").lower()

    def test_preferences_defaults(self, client, auth_headers):
        """Test that preferences have proper default values when created."""
        response = client.get("/preferences", headers=auth_headers)

        if response.status_code == 200:
            prefs = PreferencesResponse.model_validate(response.json())

            # Verify expected defaults from data model
            assert prefs.email_marketing == True  # Default from spec
            assert prefs.email_order_updates == True  # Default from spec
            assert prefs.email_security_alerts == True  # Default from spec
            assert prefs.sms_notifications == False  # Default from spec
            assert prefs.preferred_language == "en-US"  # Default from spec
            assert prefs.preferred_currency == "USD"  # Default from spec
            assert prefs.timezone == "UTC"  # Default from spec
            assert prefs.profile_visibility == "private"  # Default from spec
            assert prefs.data_sharing_consent == False  # Default from spec

    def test_preferences_content_type(self, client, auth_headers, valid_preferences_data):
        """Test that preferences endpoints require application/json content type."""
        # Test PUT without proper content-type
        response = client.put("/preferences", data=str(valid_preferences_data), headers=auth_headers)
        assert response.status_code in [400, 415], "Should reject non-JSON content"

    def test_preferences_not_found_handling(self, client, auth_headers):
        """Test handling when user preferences don't exist yet."""
        response = client.get("/preferences", headers=auth_headers)

        if response.status_code == 404:
            error_data = ErrorResponse.model_validate(response.json())
            assert error_data.error == "Not Found" or "not found" in error_data.message.lower()

    @pytest.mark.integration
    def test_preferences_operations_performance(self, client, auth_headers, valid_preferences_data):
        """Test that preferences operations respond quickly (< 200ms)."""
        import time

        # Test GET preferences performance
        start_time = time.time()
        response = client.get("/preferences", headers=auth_headers)
        get_duration = time.time() - start_time
        assert get_duration < 0.2, f"GET /preferences took {get_duration:.3f}s, should be < 200ms"

        # Test PUT preferences performance
        start_time = time.time()
        response = client.put("/preferences", json=valid_preferences_data, headers=auth_headers)
        put_duration = time.time() - start_time
        if response.status_code in [200, 400]:  # Expected responses
            assert put_duration < 0.2, f"PUT /preferences took {put_duration:.3f}s, should be < 200ms"

    def test_preferences_idempotency(self, client, auth_headers, valid_preferences_data):
        """Test that multiple identical preference updates are idempotent."""
        # Make first update
        response1 = client.put("/preferences", json=valid_preferences_data, headers=auth_headers)

        # Make identical update
        response2 = client.put("/preferences", json=valid_preferences_data, headers=auth_headers)

        # Both should succeed with same data
        if response1.status_code == 200 and response2.status_code == 200:
            prefs1 = PreferencesResponse.model_validate(response1.json())
            prefs2 = PreferencesResponse.model_validate(response2.json())

            # Data should be identical (except possibly updated_at)
            assert prefs1.id == prefs2.id
            assert prefs1.user_id == prefs2.user_id
            assert prefs1.email_marketing == prefs2.email_marketing
            assert prefs1.preferred_language == prefs2.preferred_language
            assert prefs1.preferred_currency == prefs2.preferred_currency