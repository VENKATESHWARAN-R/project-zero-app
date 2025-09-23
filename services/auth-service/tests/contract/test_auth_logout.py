"""
Contract test for POST /auth/logout endpoint.
Tests the API contract defined in auth-api.yml.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestLogoutContract:
    """Test logout endpoint contract compliance."""

    def test_logout_success_response_structure(self):
        """Test that successful logout returns correct response structure."""
        # This test should fail initially (TDD)
        logout_data = {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.example"
        }

        response = client.post("/auth/logout", json=logout_data)

        # Contract: 200 status for successful logout
        assert response.status_code == 200

        # Contract: Response must include message field
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)
        assert "logged out" in data["message"].lower()

    def test_logout_invalid_token_response(self):
        """Test response for invalid refresh token."""
        logout_data = {
            "refresh_token": "invalid_token"
        }

        response = client.post("/auth/logout", json=logout_data)

        # Contract: 400 status for invalid token
        assert response.status_code == 400

        # Contract: Error response structure
        data = response.json()
        assert "detail" in data

    def test_logout_missing_token_response(self):
        """Test response for missing refresh token."""
        logout_data = {}

        response = client.post("/auth/logout", json=logout_data)

        # Contract: 422 status for validation errors
        assert response.status_code == 422

    def test_logout_empty_token_response(self):
        """Test response for empty refresh token."""
        logout_data = {
            "refresh_token": ""
        }

        response = client.post("/auth/logout", json=logout_data)

        # Contract: 400 or 422 status for empty token
        assert response.status_code in [400, 422]

    def test_logout_malformed_token_response(self):
        """Test response for malformed JWT token."""
        logout_data = {
            "refresh_token": "not.a.jwt"
        }

        response = client.post("/auth/logout", json=logout_data)

        # Contract: 400 status for malformed token
        assert response.status_code == 400

        # Contract: Error response structure
        data = response.json()
        assert "detail" in data

    def test_logout_expired_token_response(self):
        """Test response for expired refresh token."""
        # JWT with exp claim in the past
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjAwMDAwMDAwfQ.example"
        logout_data = {
            "refresh_token": expired_token
        }

        response = client.post("/auth/logout", json=logout_data)

        # Contract: 401 status for expired token
        assert response.status_code == 401

    def test_logout_content_type_json(self):
        """Test that logout endpoint accepts JSON content type."""
        logout_data = {
            "refresh_token": "valid_token_format"
        }

        response = client.post(
            "/auth/logout",
            json=logout_data,
            headers={"Content-Type": "application/json"}
        )

        # Should not fail due to content type
        assert response.status_code in [200, 400, 401, 422]

    def test_logout_already_blacklisted_token(self):
        """Test response for token that's already blacklisted."""
        # This scenario tests idempotency of logout
        logout_data = {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.blacklisted"
        }

        response = client.post("/auth/logout", json=logout_data)

        # Contract: Should handle gracefully (200 or 400)
        assert response.status_code in [200, 400]