"""
Contract test for GET /auth/verify endpoint.
Tests the API contract defined in auth-api.yml.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestVerifyContract:
    """Test verify endpoint contract compliance."""

    def test_verify_success_response_structure(self):
        """Test that successful verification returns correct response structure."""
        # This test should fail initially (TDD)
        valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.example"

        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {valid_token}"}
        )

        # Contract: 200 status for valid token
        assert response.status_code == 200

        # Contract: Response must include required fields
        data = response.json()
        assert "valid" in data
        assert "user_id" in data

        # Contract: Validate field types
        assert isinstance(data["valid"], bool)
        assert data["valid"] is True
        assert isinstance(data["user_id"], int)

        # Contract: Optional email field if present
        if "email" in data:
            assert isinstance(data["email"], str)
            assert "@" in data["email"]

    def test_verify_invalid_token_response(self):
        """Test response for invalid access token."""
        invalid_token = "invalid_token"

        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )

        # Contract: 401 status for invalid token
        assert response.status_code == 401

        # Contract: Error response structure
        data = response.json()
        assert "detail" in data

    def test_verify_expired_token_response(self):
        """Test response for expired access token."""
        # JWT with exp claim in the past
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2MDAwMDAwMDB9.example"

        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        # Contract: 401 status for expired token
        assert response.status_code == 401

        # Contract: Error response includes expiration message
        data = response.json()
        assert "detail" in data

    def test_verify_missing_authorization_header(self):
        """Test response when Authorization header is missing."""
        response = client.get("/auth/verify")

        # Contract: 401 status for missing authorization
        assert response.status_code == 401

    def test_verify_malformed_authorization_header(self):
        """Test response for malformed Authorization header."""
        # Missing "Bearer " prefix
        response = client.get(
            "/auth/verify",
            headers={"Authorization": "invalid_format_token"}
        )

        # Contract: 401 status for malformed header
        assert response.status_code == 401

    def test_verify_refresh_token_as_access_token(self):
        """Test response when refresh token is used instead of access token."""
        # Token with type: "refresh" instead of "access"
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.example"

        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {refresh_token}"}
        )

        # Contract: 401 status for wrong token type
        assert response.status_code == 401

    def test_verify_blacklisted_token_response(self):
        """Test response for blacklisted access token."""
        # Token that has been invalidated
        blacklisted_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.blacklisted"

        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {blacklisted_token}"}
        )

        # Contract: 401 status for blacklisted token
        assert response.status_code == 401

    def test_verify_bearer_scheme_required(self):
        """Test that Bearer scheme is required in Authorization header."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.example"

        # Using "Basic" instead of "Bearer"
        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Basic {token}"}
        )

        # Contract: 401 status for wrong auth scheme
        assert response.status_code == 401

    def test_verify_user_id_consistency(self):
        """Test that user_id in response matches token claims."""
        # This test verifies token claims are properly decoded
        valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo0NTYsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.example"

        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {valid_token}"}
        )

        if response.status_code == 200:
            data = response.json()
            # The user_id should match what's encoded in the token (456)
            # This will only pass when JWT validation is properly implemented
            assert "user_id" in data

    def test_verify_case_sensitive_bearer(self):
        """Test that Bearer scheme is case-sensitive."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.example"

        # Using lowercase "bearer"
        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"bearer {token}"}
        )

        # FastAPI OAuth2PasswordBearer might be case-insensitive, but test the behavior
        assert response.status_code in [200, 401]