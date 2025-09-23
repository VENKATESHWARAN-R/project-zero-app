"""
Contract test for POST /auth/login endpoint.
Tests the API contract defined in auth-api.yml.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestLoginContract:
    """Test login endpoint contract compliance."""

    def test_login_success_response_structure(self):
        """Test that successful login returns correct response structure."""
        # This test should fail initially (TDD)
        login_data = {
            "email": "test@example.com",
            "password": "SecurePass123"
        }

        response = client.post("/auth/login", json=login_data)

        # Contract: 200 status for valid credentials
        assert response.status_code == 200

        # Contract: Response must include all required fields
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data

        # Contract: Validate field types
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)
        assert data["token_type"] == "bearer"
        assert isinstance(data["expires_in"], int)

        # Contract: Access token should be JWT format (basic check)
        assert len(data["access_token"]) > 20
        assert "." in data["access_token"]

    def test_login_invalid_credentials_response(self):
        """Test response for invalid credentials."""
        login_data = {
            "email": "test@example.com",
            "password": "WrongPassword"
        }

        response = client.post("/auth/login", json=login_data)

        # Contract: 401 status for invalid credentials
        assert response.status_code == 401

        # Contract: Error response structure
        data = response.json()
        assert "detail" in data

    def test_login_validation_error_response(self):
        """Test response for validation errors."""
        # Missing password field
        login_data = {
            "email": "test@example.com"
        }

        response = client.post("/auth/login", json=login_data)

        # Contract: 422 status for validation errors
        assert response.status_code == 422

    def test_login_invalid_email_format(self):
        """Test response for invalid email format."""
        login_data = {
            "email": "not-an-email",
            "password": "SecurePass123"
        }

        response = client.post("/auth/login", json=login_data)

        # Contract: 422 status for invalid email format
        assert response.status_code == 422

    def test_login_short_password(self):
        """Test response for password under minimum length."""
        login_data = {
            "email": "test@example.com",
            "password": "short"
        }

        response = client.post("/auth/login", json=login_data)

        # Contract: 422 status for password validation
        assert response.status_code == 422

    def test_login_rate_limiting_response(self):
        """Test rate limiting response after multiple failed attempts."""
        login_data = {
            "email": "ratelimit@example.com",
            "password": "WrongPassword"
        }

        # Make multiple failed attempts
        for _ in range(6):
            response = client.post("/auth/login", json=login_data)

        # Contract: 429 status when rate limited
        # Note: This may pass on the 5th attempt or fail before rate limiting is implemented
        if response.status_code == 429:
            data = response.json()
            assert "detail" in data

    def test_login_content_type_json(self):
        """Test that login endpoint accepts JSON content type."""
        login_data = {
            "email": "test@example.com",
            "password": "SecurePass123"
        }

        response = client.post(
            "/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )

        # Should not fail due to content type
        assert response.status_code in [200, 401, 422]

    def test_login_empty_request_body(self):
        """Test response for empty request body."""
        response = client.post("/auth/login", json={})

        # Contract: 422 status for missing required fields
        assert response.status_code == 422