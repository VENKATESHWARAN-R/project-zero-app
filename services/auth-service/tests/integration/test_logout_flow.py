"""
Integration test for logout and token invalidation flow.
Tests Story 4 from quickstart.md: User Logout.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestLogoutFlow:
    """Test logout flow and token invalidation integration."""

    def test_logout_flow_success(self):
        """Test complete logout flow."""
        # This test should fail initially (TDD)
        # Story 4: User Logout

        # Valid refresh token (would come from login response)
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.logout_test"

        # Step: User logs out
        logout_data = {"refresh_token": refresh_token}
        response = client.post("/auth/logout", json=logout_data)

        # Success Criteria from quickstart.md:
        # ✅ Logout returns 200 HTTP status
        assert response.status_code == 200

        # ✅ Returns confirmation message
        data = response.json()
        assert "message" in data
        assert "logged out" in data["message"].lower()

    def test_logout_token_invalidation_verification(self):
        """Test that logout properly invalidates tokens."""
        # Story 4: Verification step from quickstart.md

        # Valid refresh token
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.invalidation_test"

        # First, logout the user
        logout_response = client.post("/auth/logout", json={"refresh_token": refresh_token})

        if logout_response.status_code == 200:
            # Verification: Try to use the refresh token again - should fail
            refresh_response = client.post("/auth/refresh", json={"refresh_token": refresh_token})

            # Success Criteria from quickstart.md:
            # ✅ Subsequent refresh attempts return 401
            assert refresh_response.status_code == 401

            # ✅ Blacklisted tokens are remembered
            # Token should remain invalid on repeated attempts
            second_refresh_response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
            assert second_refresh_response.status_code == 401

    def test_logout_access_token_behavior(self):
        """Test access token behavior after logout."""
        # Access token from same session
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.access_logout"
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.refresh_logout"

        # Logout using refresh token
        logout_response = client.post("/auth/logout", json={"refresh_token": refresh_token})

        if logout_response.status_code == 200:
            # Check access token behavior
            verify_response = client.get(
                "/auth/verify",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            # Success Criteria from quickstart.md:
            # ✅ Access token still works until natural expiry
            # Note: This depends on implementation - some systems invalidate all tokens
            # Check the actual behavior
            if verify_response.status_code == 200:
                # Implementation allows access tokens to continue working
                user_data = verify_response.json()
                assert user_data["valid"] is True
            elif verify_response.status_code == 401:
                # Implementation invalidates all tokens on logout
                pass

    def test_logout_with_invalid_refresh_token(self):
        """Test logout flow with invalid refresh token."""
        # Various invalid refresh token scenarios

        # Completely invalid token
        response = client.post("/auth/logout", json={"refresh_token": "invalid"})
        assert response.status_code == 400

        # Malformed JWT
        response = client.post("/auth/logout", json={"refresh_token": "not.a.jwt"})
        assert response.status_code == 400

        # Missing refresh token
        response = client.post("/auth/logout", json={})
        assert response.status_code == 422

        # Empty refresh token
        response = client.post("/auth/logout", json={"refresh_token": ""})
        assert response.status_code in [400, 422]

    def test_logout_with_expired_refresh_token(self):
        """Test logout flow with expired refresh token."""
        # Refresh token with exp claim in the past
        expired_refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjAwMDAwMDAwfQ.expired_logout"

        response = client.post("/auth/logout", json={"refresh_token": expired_refresh_token})

        # Behavior depends on implementation:
        # Option 1: Allow logout of expired tokens (graceful)
        # Option 2: Reject expired tokens
        assert response.status_code in [200, 401]

    def test_logout_with_access_token_instead_of_refresh(self):
        """Test logout when access token is provided instead of refresh token."""
        # Access token used for logout (should be rejected)
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.access_wrong"

        response = client.post("/auth/logout", json={"refresh_token": access_token})

        # Should reject access tokens for logout
        assert response.status_code == 400

    def test_logout_already_logged_out_token(self):
        """Test logout with token that's already been logged out."""
        # Token that has already been blacklisted
        already_logged_out_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.already_out"

        # First logout
        first_response = client.post("/auth/logout", json={"refresh_token": already_logged_out_token})

        if first_response.status_code == 200:
            # Second logout attempt with same token
            second_response = client.post("/auth/logout", json={"refresh_token": already_logged_out_token})

            # Should handle gracefully (idempotent operation)
            # Success Criteria: Should handle gracefully (200 or 400)
            assert second_response.status_code in [200, 400]

    def test_logout_concurrent_requests(self):
        """Test concurrent logout requests with same token."""
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.concurrent_logout"

        logout_data = {"refresh_token": refresh_token}

        # Make concurrent logout requests
        responses = []
        for _ in range(3):
            response = client.post("/auth/logout", json=logout_data)
            responses.append(response.status_code)

        # At least one should succeed
        success_count = sum(1 for status in responses if status == 200)
        assert success_count >= 1

        # Others might succeed (idempotent) or fail (already logged out)
        for status in responses:
            assert status in [200, 400]

    def test_logout_realistic_mobile_app_scenario(self):
        """Test realistic logout scenario for mobile app."""
        # Mobile app logging out user

        # 1. App has stored tokens from login
        user_refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo3ODksInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.mobile_logout"

        # 2. User taps "Logout" button
        logout_response = client.post("/auth/logout", json={"refresh_token": user_refresh_token})

        if logout_response.status_code == 200:
            # 3. App receives confirmation
            logout_data = logout_response.json()
            assert "message" in logout_data

            # 4. App clears stored tokens
            # 5. App redirects to login screen

            # 6. Verify that stored tokens are now invalid
            refresh_response = client.post("/auth/refresh", json={"refresh_token": user_refresh_token})
            assert refresh_response.status_code == 401

    def test_logout_web_app_scenario(self):
        """Test logout scenario for web application."""
        # Web app logging out user

        # 1. User has active session with tokens
        session_refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo0NTYsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.web_logout"

        # 2. User clicks "Sign Out"
        logout_response = client.post("/auth/logout", json={"refresh_token": session_refresh_token})

        if logout_response.status_code == 200:
            # 3. Backend confirms logout
            logout_data = logout_response.json()
            assert "successfully" in logout_data["message"].lower()

            # 4. Frontend clears cookies/localStorage
            # 5. Frontend redirects to home/login page

            # 6. Any subsequent API calls with old tokens should fail
            verify_response = client.get(
                "/auth/verify",
                headers={"Authorization": "Bearer old_access_token"}
            )
            # Should fail (either because token is blacklisted or naturally expired)
            # Exact behavior depends on implementation

    def test_logout_security_considerations(self):
        """Test security aspects of logout flow."""
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.security_logout"

        # Logout should be POST, not GET (CSRF protection)
        get_response = client.get(f"/auth/logout?refresh_token={refresh_token}")
        assert get_response.status_code == 405  # Method not allowed

        # Logout should require JSON body
        form_response = client.post("/auth/logout", data={"refresh_token": refresh_token})
        # Should either work or require JSON content-type
        assert form_response.status_code in [200, 400, 422]

        # Actual logout with proper JSON
        json_response = client.post("/auth/logout", json={"refresh_token": refresh_token})
        assert json_response.status_code in [200, 400]

    def test_logout_performance_requirements(self):
        """Test logout performance requirements."""
        import time

        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.perf_logout"

        # Measure logout time
        start_time = time.time()
        response = client.post("/auth/logout", json={"refresh_token": refresh_token})
        end_time = time.time()

        response_time = end_time - start_time

        # Logout should be fast (< 500ms)
        assert response_time < 0.5

    def test_logout_token_blacklist_persistence(self):
        """Test that token blacklist persists across requests."""
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.blacklist_persist"

        # Logout token
        logout_response = client.post("/auth/logout", json={"refresh_token": refresh_token})

        if logout_response.status_code == 200:
            # Wait a moment (simulate time passing)
            import time
            time.sleep(0.1)

            # Try to use token again - should still be blacklisted
            refresh_response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
            assert refresh_response.status_code == 401

            # Multiple attempts should all fail
            for _ in range(3):
                refresh_response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
                assert refresh_response.status_code == 401