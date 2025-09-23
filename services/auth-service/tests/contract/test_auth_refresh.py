"""
Contract test for POST /auth/refresh endpoint.
Tests the API contract defined in auth-api.yml.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestRefreshContract:
    """Test refresh endpoint contract compliance."""

    def test_refresh_success_response_structure(self):
        """Test that successful refresh returns correct response structure."""
        # This test should fail initially (TDD)
        refresh_data = {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.example"
        }

        response = client.post("/auth/refresh", json=refresh_data)

        # Contract: 200 status for valid refresh token
        assert response.status_code == 200

        # Contract: Response must include required fields
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data

        # Contract: Validate field types
        assert isinstance(data["access_token"], str)
        assert data["token_type"] == "bearer"
        assert isinstance(data["expires_in"], int)

        # Contract: Access token should be JWT format
        assert len(data["access_token"]) > 20
        assert "." in data["access_token"]

        # Contract: expires_in should be reasonable (e.g., 900 seconds = 15 minutes)
        assert data["expires_in"] > 0
        assert data["expires_in"] <= 3600  # Max 1 hour

    def test_refresh_invalid_token_response(self):
        """Test response for invalid refresh token."""
        refresh_data = {
            "refresh_token": "invalid_token"
        }

        response = client.post("/auth/refresh", json=refresh_data)

        # Contract: 401 status for invalid token
        assert response.status_code == 401

        # Contract: Error response structure
        data = response.json()
        assert "detail" in data

    def test_refresh_expired_token_response(self):
        """Test response for expired refresh token."""
        # JWT with exp claim in the past
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjAwMDAwMDAwfQ.example"
        refresh_data = {
            "refresh_token": expired_token
        }

        response = client.post("/auth/refresh", json=refresh_data)

        # Contract: 401 status for expired token
        assert response.status_code == 401

        # Contract: Error response includes expiration message
        data = response.json()
        assert "detail" in data
        assert "expired" in data["detail"].lower()

    def test_refresh_missing_token_response(self):
        """Test response for missing refresh token."""
        refresh_data = {}

        response = client.post("/auth/refresh", json=refresh_data)

        # Contract: 422 status for validation errors
        assert response.status_code == 422

    def test_refresh_malformed_token_response(self):
        """Test response for malformed JWT token."""
        refresh_data = {
            "refresh_token": "not.a.jwt"
        }

        response = client.post("/auth/refresh", json=refresh_data)

        # Contract: 401 status for malformed token
        assert response.status_code == 401

    def test_refresh_access_token_as_refresh_token(self):
        """Test response when access token is used instead of refresh token."""
        # Token with type: "access" instead of "refresh"
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.example"
        refresh_data = {
            "refresh_token": access_token
        }

        response = client.post("/auth/refresh", json=refresh_data)

        # Contract: 401 status for wrong token type
        assert response.status_code == 401

    def test_refresh_blacklisted_token_response(self):
        """Test response for blacklisted refresh token."""
        # Token that has been logged out
        blacklisted_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.blacklisted"
        refresh_data = {
            "refresh_token": blacklisted_token
        }

        response = client.post("/auth/refresh", json=refresh_data)

        # Contract: 401 status for blacklisted token
        assert response.status_code == 401

    def test_refresh_content_type_json(self):
        """Test that refresh endpoint accepts JSON content type."""
        refresh_data = {
            "refresh_token": "valid_format_token"
        }

        response = client.post(
            "/auth/refresh",
            json=refresh_data,
            headers={"Content-Type": "application/json"}
        )

        # Should not fail due to content type
        assert response.status_code in [200, 401, 422]

    def test_refresh_new_token_different_from_old(self):
        """Test that new access token is different from any previous tokens."""
        refresh_data = {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.unique"
        }

        response = client.post("/auth/refresh", json=refresh_data)

        if response.status_code == 200:
            data = response.json()
            # New access token should not be the same as refresh token
            assert data["access_token"] != refresh_data["refresh_token"]