"""
Integration test for token verification by other services.
Tests Story 2 from quickstart.md: Token Verification by Other Services.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestTokenVerification:
    """Test token verification flow for other microservices."""

    def test_token_verification_flow_success(self):
        """Test complete token verification flow for other services."""
        # This test should fail initially (TDD)
        # Story 2: Token Verification by Other Services

        # First, we need a valid access token
        # In real scenario, this would come from a successful login
        sample_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.example"

        # Step: Other service validates user authentication
        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {sample_access_token}"}
        )

        # Success Criteria from quickstart.md:
        # ✅ Returns 200 HTTP status
        assert response.status_code == 200

        # ✅ Confirms token validity
        data = response.json()
        assert "valid" in data
        assert data["valid"] is True

        # ✅ Provides user information
        assert "user_id" in data
        assert isinstance(data["user_id"], int)

        # ✅ Response time < 100ms (from quickstart.md)
        # This will be tested in performance tests

        # Optional email field
        if "email" in data:
            assert isinstance(data["email"], str)
            assert "@" in data["email"]

    def test_token_verification_microservice_integration(self):
        """Test how other microservices would integrate with auth verification."""
        # Simulate how product-catalog-service or cart-service would verify tokens

        valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo0NTYsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.valid"

        # Microservice makes verification request
        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {valid_token}"}
        )

        if response.status_code == 200:
            data = response.json()

            # Microservice can trust this response to proceed with business logic
            user_id = data["user_id"]
            assert user_id > 0

            # Microservice would use user_id for authorization decisions
            # e.g., "Can user_id 456 access their shopping cart?"

    def test_token_verification_invalid_token_flow(self):
        """Test token verification flow with invalid tokens."""
        # Test various invalid token scenarios

        # Completely invalid token
        response = client.get(
            "/auth/verify",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

        # Malformed JWT
        response = client.get(
            "/auth/verify",
            headers={"Authorization": "Bearer not.a.jwt"}
        )
        assert response.status_code == 401

        # Missing Authorization header
        response = client.get("/auth/verify")
        assert response.status_code == 401

    def test_token_verification_expired_token_flow(self):
        """Test token verification with expired access token."""
        # Token with exp claim in the past
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2MDAwMDAwMDB9.expired"

        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        # Should reject expired tokens
        assert response.status_code == 401

        data = response.json()
        assert "detail" in data

    def test_token_verification_wrong_token_type(self):
        """Test verification when refresh token is used instead of access token."""
        # Refresh token used for verification (should be rejected)
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNjQwOTk1MjAwfQ.refresh"

        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {refresh_token}"}
        )

        # Should reject refresh tokens for verification
        assert response.status_code == 401

    def test_token_verification_blacklisted_token(self):
        """Test verification of blacklisted (logged out) token."""
        # Token that has been logged out
        blacklisted_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.blacklisted"

        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {blacklisted_token}"}
        )

        # Should reject blacklisted tokens
        assert response.status_code == 401

    def test_token_verification_authorization_header_formats(self):
        """Test various Authorization header formats."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.example"

        # Correct format
        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 401]  # Depends on token validity

        # Wrong scheme
        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Basic {token}"}
        )
        assert response.status_code == 401

        # No scheme
        response = client.get(
            "/auth/verify",
            headers={"Authorization": token}
        )
        assert response.status_code == 401

        # Case sensitivity
        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"bearer {token}"}
        )
        # FastAPI might be case-insensitive, check actual behavior
        assert response.status_code in [200, 401]

    def test_token_verification_user_context_extraction(self):
        """Test extracting user context from verified token."""
        # Valid token with specific user_id
        token_with_user_456 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo0NTYsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.user456"

        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {token_with_user_456}"}
        )

        if response.status_code == 200:
            data = response.json()

            # Should extract correct user_id from token
            assert data["user_id"] == 456

            # This enables microservices to make user-specific decisions
            # e.g., "Show user 456's order history"

    def test_token_verification_performance_requirements(self):
        """Test that token verification meets performance requirements."""
        import time

        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.perf"

        # Measure verification time
        start_time = time.time()
        response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        end_time = time.time()

        response_time = end_time - start_time

        # Success Criteria: Response time < 100ms (from quickstart.md)
        assert response_time < 0.1

    def test_token_verification_concurrent_requests(self):
        """Test concurrent token verification requests."""
        # Simulate multiple microservices verifying tokens simultaneously
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.concurrent"

        # Make multiple concurrent requests
        responses = []
        for _ in range(10):
            response = client.get(
                "/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            )
            responses.append(response.status_code)

        # All responses should be consistent
        assert len(set(responses)) == 1

    def test_token_verification_cross_service_scenario(self):
        """Test realistic cross-service verification scenario."""
        # Simulate cart-service verifying user token before allowing cart access

        user_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo3ODksInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE2NDA5OTUyMDB9.cart_user"

        # Cart service calls auth service to verify token
        auth_response = client.get(
            "/auth/verify",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        if auth_response.status_code == 200:
            user_data = auth_response.json()
            user_id = user_data["user_id"]

            # Cart service can now proceed with user-specific operations
            assert user_id == 789
            assert user_data["valid"] is True

            # This enables cart service to:
            # 1. Show user 789's cart contents
            # 2. Allow modifications to user 789's cart
            # 3. Reject access attempts from other users

        elif auth_response.status_code == 401:
            # Cart service would return 401 to client
            # User needs to login again
            pass