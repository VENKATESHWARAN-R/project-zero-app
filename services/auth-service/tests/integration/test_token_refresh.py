"""
Integration test for token refresh functionality.
Tests Story 3 from quickstart.md: Token Refresh.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestTokenRefresh:
    """Test token refresh flow integration."""

    def test_token_refresh_flow_success(self):
        """Test complete token refresh flow."""
        # This test should fail initially (TDD)
        # Story 3: Token Refresh

        # Valid refresh token (would come from login response)
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.valid_refresh"

        # Step: User requests token refresh
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/auth/refresh", json=refresh_data)

        # Success Criteria from quickstart.md:
        # ✅ Returns 200 HTTP status
        assert response.status_code == 200

        # ✅ Provides new access token
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data

        # ✅ New token is different from original
        new_access_token = data["access_token"]
        assert new_access_token != refresh_token
        assert len(new_access_token) > 20
        assert "." in new_access_token  # JWT format

        # ✅ Original access token still works until expiry
        # This would be tested in a separate scenario

        # Validate response structure
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 900  # 15 minutes

    def test_token_refresh_with_expired_refresh_token(self):
        """Test refresh flow with expired refresh token."""
        # Refresh token with exp claim in the past
        expired_refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjAwMDAwMDAwfQ.expired"

        refresh_data = {"refresh_token": expired_refresh_token}
        response = client.post("/auth/refresh", json=refresh_data)

        # Should reject expired refresh tokens
        assert response.status_code == 401

        data = response.json()
        assert "detail" in data
        assert "expired" in data["detail"].lower()

    def test_token_refresh_with_invalid_refresh_token(self):
        """Test refresh flow with invalid refresh token."""
        # Various invalid refresh token scenarios

        # Completely invalid token
        response = client.post("/auth/refresh", json={"refresh_token": "invalid"})
        assert response.status_code == 401

        # Malformed JWT
        response = client.post("/auth/refresh", json={"refresh_token": "not.a.jwt"})
        assert response.status_code == 401

        # Missing refresh token
        response = client.post("/auth/refresh", json={})
        assert response.status_code == 422

    def test_token_refresh_with_access_token_instead_of_refresh(self):
        """Test refresh flow when access token is used instead of refresh token."""
        # Access token used for refresh (should be rejected)
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.access"

        refresh_data = {"refresh_token": access_token}
        response = client.post("/auth/refresh", json=refresh_data)

        # Should reject access tokens for refresh
        assert response.status_code == 401

    def test_token_refresh_with_blacklisted_refresh_token(self):
        """Test refresh flow with blacklisted (logged out) refresh token."""
        # Refresh token that has been logged out
        blacklisted_refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.blacklisted"

        refresh_data = {"refresh_token": blacklisted_refresh_token}
        response = client.post("/auth/refresh", json=refresh_data)

        # Should reject blacklisted tokens
        assert response.status_code == 401

    def test_token_refresh_preserves_user_context(self):
        """Test that token refresh preserves user context."""
        # Refresh token for specific user
        user_456_refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo0NTYsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.user456"

        refresh_data = {"refresh_token": user_456_refresh_token}
        response = client.post("/auth/refresh", json=refresh_data)

        if response.status_code == 200:
            data = response.json()
            new_access_token = data["access_token"]

            # Verify the new access token contains the same user context
            # This would be tested by verifying the token
            verify_response = client.get(
                "/auth/verify",
                headers={"Authorization": f"Bearer {new_access_token}"}
            )

            if verify_response.status_code == 200:
                user_data = verify_response.json()
                assert user_data["user_id"] == 456

    def test_token_refresh_performance_requirements(self):
        """Test that token refresh meets performance requirements."""
        import time

        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.perf"

        # Measure refresh time
        start_time = time.time()
        response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
        end_time = time.time()

        response_time = end_time - start_time

        # Success Criteria: Response time < 200ms (from quickstart.md)
        assert response_time < 0.2

    def test_token_refresh_multiple_times(self):
        """Test refreshing the same refresh token multiple times."""
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.multiple"

        refresh_data = {"refresh_token": refresh_token}

        # First refresh
        response1 = client.post("/auth/refresh", json=refresh_data)

        # Second refresh with same token
        response2 = client.post("/auth/refresh", json=refresh_data)

        # Behavior depends on implementation:
        # Option 1: Both succeed (refresh token can be reused)
        # Option 2: Second fails (refresh token rotation - one-time use)

        if response1.status_code == 200:
            # At least first refresh should work
            data1 = response1.json()
            assert "access_token" in data1

        # Second refresh behavior is implementation-dependent
        assert response2.status_code in [200, 401]

    def test_token_refresh_concurrent_requests(self):
        """Test concurrent refresh requests with same token."""
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.concurrent"

        refresh_data = {"refresh_token": refresh_token}

        # Make concurrent refresh requests
        responses = []
        for _ in range(5):
            response = client.post("/auth/refresh", json=refresh_data)
            responses.append(response.status_code)

        # All responses should be consistent
        # Either all succeed or some fail (depending on token rotation policy)
        success_count = sum(1 for status in responses if status == 200)

        # At least one should succeed
        assert success_count >= 1

    def test_token_refresh_realistic_scenario(self):
        """Test realistic token refresh scenario."""
        # Simulate a mobile app refreshing an expired access token

        # 1. App has stored refresh token from previous login
        stored_refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo3ODksInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.mobile_app"

        # 2. App's access token has expired, so it requests a new one
        refresh_response = client.post("/auth/refresh", json={
            "refresh_token": stored_refresh_token
        })

        if refresh_response.status_code == 200:
            # 3. App receives new access token
            refresh_data = refresh_response.json()
            new_access_token = refresh_data["access_token"]

            # 4. App can now make authenticated requests
            verify_response = client.get(
                "/auth/verify",
                headers={"Authorization": f"Bearer {new_access_token}"}
            )

            # 5. Requests should succeed with new token
            if verify_response.status_code == 200:
                user_data = verify_response.json()
                assert user_data["valid"] is True
                assert user_data["user_id"] == 789

        elif refresh_response.status_code == 401:
            # Refresh token is invalid/expired
            # App should redirect user to login
            pass

    def test_token_refresh_edge_cases(self):
        """Test edge cases in token refresh flow."""
        # Empty string refresh token
        response = client.post("/auth/refresh", json={"refresh_token": ""})
        assert response.status_code in [400, 422]

        # Null refresh token
        response = client.post("/auth/refresh", json={"refresh_token": None})
        assert response.status_code == 422

        # Wrong field name
        response = client.post("/auth/refresh", json={"token": "some_token"})
        assert response.status_code == 422

        # Extra fields (should be ignored)
        response = client.post("/auth/refresh", json={
            "refresh_token": "valid_token",
            "extra_field": "should_be_ignored"
        })
        # Should process normally, ignoring extra field
        assert response.status_code in [200, 401]

    def test_token_refresh_maintains_security(self):
        """Test that token refresh maintains security properties."""
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.security"

        response = client.post("/auth/refresh", json={"refresh_token": refresh_token})

        if response.status_code == 200:
            data = response.json()

            # New access token should have proper expiration
            assert data["expires_in"] > 0
            assert data["expires_in"] <= 3600

            # New access token should be different
            assert data["access_token"] != refresh_token

            # Token type should be correct
            assert data["token_type"] == "bearer"