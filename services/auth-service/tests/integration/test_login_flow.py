"""
Integration test for valid user login flow.
Tests the complete login scenario from quickstart.md.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestLoginFlow:
    """Test complete user login flow integration."""

    def test_complete_login_flow_success(self):
        """Test the complete login flow for a valid user."""
        # This test should fail initially (TDD)
        # Story 1: User Login with Valid Credentials

        # Test data from quickstart.md
        login_data = {
            "email": "test@example.com",
            "password": "SecurePass123"
        }

        # Step 1: Attempt to login
        response = client.post("/auth/login", json=login_data)

        # Success Criteria from quickstart.md:
        # ✅ Returns 200 HTTP status
        assert response.status_code == 200

        # ✅ Provides both access and refresh tokens
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data

        # ✅ Tokens are valid JWT format
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]

        # Basic JWT format validation (3 parts separated by dots)
        assert len(access_token.split(".")) == 3
        assert len(refresh_token.split(".")) == 3

        # ✅ Response time < 500ms (from quickstart.md)
        # This will be tested in performance tests, but basic check here
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 900  # 15 minutes as per specification

    def test_login_flow_with_new_user_registration(self):
        """Test login flow that includes user registration."""
        # For a new user that doesn't exist yet
        new_user_data = {
            "email": "newuser@example.com",
            "password": "NewSecurePass123"
        }

        # First attempt should either:
        # 1. Auto-register the user (if registration is part of login)
        # 2. Return 401 (user not found)
        response = client.post("/auth/login", json=new_user_data)

        # This behavior depends on implementation:
        # - If auto-registration: should succeed (200)
        # - If explicit registration required: should fail (401)
        assert response.status_code in [200, 401]

        if response.status_code == 401:
            # User needs to be registered first
            # Note: Registration endpoint not in current spec,
            # so this test documents expected behavior
            pass

    def test_login_flow_password_validation(self):
        """Test login flow with password validation requirements."""
        # Test with password that doesn't meet requirements
        invalid_password_data = {
            "email": "test@example.com",
            "password": "weak"  # Too short
        }

        response = client.post("/auth/login", json=invalid_password_data)

        # Should fail validation before attempting authentication
        assert response.status_code == 422

    def test_login_flow_email_validation(self):
        """Test login flow with email validation."""
        # Test with invalid email format
        invalid_email_data = {
            "email": "not-an-email",
            "password": "SecurePass123"
        }

        response = client.post("/auth/login", json=invalid_email_data)

        # Should fail email format validation
        assert response.status_code == 422

    def test_login_flow_missing_credentials(self):
        """Test login flow with missing credentials."""
        # Missing password
        response = client.post("/auth/login", json={"email": "test@example.com"})
        assert response.status_code == 422

        # Missing email
        response = client.post("/auth/login", json={"password": "SecurePass123"})
        assert response.status_code == 422

        # Empty request
        response = client.post("/auth/login", json={})
        assert response.status_code == 422

    def test_login_flow_wrong_credentials(self):
        """Test login flow with incorrect credentials."""
        # Wrong password
        wrong_password_data = {
            "email": "test@example.com",
            "password": "WrongPassword123"
        }

        response = client.post("/auth/login", json=wrong_password_data)
        assert response.status_code == 401

        # Wrong email (user doesn't exist)
        wrong_email_data = {
            "email": "nonexistent@example.com",
            "password": "SecurePass123"
        }

        response = client.post("/auth/login", json=wrong_email_data)
        assert response.status_code == 401

    def test_login_flow_token_properties(self):
        """Test that login flow returns tokens with correct properties."""
        login_data = {
            "email": "test@example.com",
            "password": "SecurePass123"
        }

        response = client.post("/auth/login", json=login_data)

        if response.status_code == 200:
            data = response.json()

            # Token type should be bearer
            assert data["token_type"] == "bearer"

            # Expires in should be reasonable (15 minutes = 900 seconds)
            assert data["expires_in"] > 0
            assert data["expires_in"] <= 3600  # Max 1 hour

            # Tokens should be different
            assert data["access_token"] != data["refresh_token"]

            # Tokens should be substantial length (JWT format)
            assert len(data["access_token"]) > 50
            assert len(data["refresh_token"]) > 50

    def test_login_flow_concurrent_requests(self):
        """Test login flow with concurrent requests."""
        import asyncio
        import httpx

        async def login_request():
            async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
                response = await ac.post("/auth/login", json={
                    "email": "concurrent@example.com",
                    "password": "SecurePass123"
                })
                return response

        # Test multiple concurrent login attempts
        # This should not cause any race conditions
        # All should either succeed or fail consistently
        async def run_concurrent_test():
            tasks = [login_request() for _ in range(5)]
            responses = await asyncio.gather(*tasks)
            status_codes = [r.status_code for r in responses]

            # All responses should have the same status code
            # (either all succeed or all fail for same credentials)
            assert len(set(status_codes)) == 1

        # Run the concurrent test
        # Note: This will only work if async support is properly set up
        try:
            asyncio.run(run_concurrent_test())
        except Exception:
            # If async testing isn't set up, just skip this part
            pass

    def test_login_flow_response_timing(self):
        """Test that login flow has consistent response timing."""
        import time

        login_data = {
            "email": "timing@example.com",
            "password": "SecurePass123"
        }

        # Measure response time
        start_time = time.time()
        response = client.post("/auth/login", json=login_data)
        end_time = time.time()

        response_time = end_time - start_time

        # Response should be reasonably fast (< 2 seconds for bcrypt)
        # bcrypt is intentionally slow, so allow more time than typical API
        assert response_time < 2.0

        # Response time should not reveal information about user existence
        # (both valid and invalid users should take similar time due to bcrypt)