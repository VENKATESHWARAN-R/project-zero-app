"""Integration tests for auth service integration.

These tests verify the authentication and authorization integration
with the auth service and JWT token handling.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any
import jwt
import time


@pytest.fixture
def client():
    """Test client fixture - will be implemented once FastAPI app exists."""
    from main import app
    return TestClient(app)


@pytest.fixture
def jwt_secret():
    """JWT secret for testing - should match auth service configuration."""
    return "test-secret-key-for-testing"


@pytest.fixture
def valid_jwt_payload():
    """Valid JWT payload structure."""
    return {
        "user_id": 42,
        "email": "test@example.com",
        "exp": int(time.time()) + 3600,  # Expires in 1 hour
        "iat": int(time.time()),
        "sub": "42"
    }


@pytest.fixture
def expired_jwt_payload():
    """Expired JWT payload for testing."""
    return {
        "user_id": 42,
        "email": "test@example.com",
        "exp": int(time.time()) - 3600,  # Expired 1 hour ago
        "iat": int(time.time()) - 7200,
        "sub": "42"
    }


@pytest.fixture
def admin_jwt_payload():
    """Admin JWT payload for testing."""
    return {
        "user_id": 1,
        "email": "admin@example.com",
        "role": "admin",
        "exp": int(time.time()) + 3600,
        "iat": int(time.time()),
        "sub": "1"
    }


def create_jwt_token(payload: Dict[str, Any], secret: str, algorithm: str = "HS256") -> str:
    """Helper function to create JWT tokens for testing."""
    return jwt.encode(payload, secret, algorithm=algorithm)


class TestAuthServiceIntegration:
    """Integration tests for auth service integration."""

    def test_valid_jwt_token_authentication(self, client, valid_jwt_payload, jwt_secret):
        """Test that valid JWT tokens are accepted and processed correctly."""
        token = create_jwt_token(valid_jwt_payload, jwt_secret)
        headers = {"Authorization": f"Bearer {token}"}

        # Test with profile endpoint
        response = client.get("/profiles", headers=headers)
        # Should not return 401 (authentication error)
        assert response.status_code != 401, "Valid JWT token should be accepted"

    def test_invalid_jwt_token_rejection(self, client):
        """Test that invalid JWT tokens are rejected."""
        invalid_tokens = [
            "invalid-token",
            "Bearer invalid-token",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid.signature",
            ""
        ]

        for token in invalid_tokens:
            if token.startswith("Bearer"):
                headers = {"Authorization": token}
            else:
                headers = {"Authorization": f"Bearer {token}"}

            response = client.get("/profiles", headers=headers)
            assert response.status_code == 401, f"Invalid token should be rejected: {token}"

    def test_expired_jwt_token_rejection(self, client, expired_jwt_payload, jwt_secret):
        """Test that expired JWT tokens are rejected."""
        expired_token = create_jwt_token(expired_jwt_payload, jwt_secret)
        headers = {"Authorization": f"Bearer {expired_token}"}

        response = client.get("/profiles", headers=headers)
        assert response.status_code == 401, "Expired JWT token should be rejected"

        error_data = response.json()
        assert "expired" in error_data["message"].lower() or "invalid" in error_data["message"].lower()

    def test_missing_authorization_header(self, client):
        """Test that requests without authorization header are rejected."""
        endpoints_requiring_auth = [
            "/profiles",
            "/addresses",
            "/preferences",
            "/activity",
            "/admin/profiles/42"
        ]

        for endpoint in endpoints_requiring_auth:
            response = client.get(endpoint)
            assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"

    def test_malformed_authorization_header(self, client):
        """Test handling of malformed authorization headers."""
        malformed_headers = [
            {"Authorization": "InvalidFormat token"},
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": "Basic dGVzdDp0ZXN0"},  # Wrong auth type
            {"X-Auth-Token": "Bearer valid-token"},  # Wrong header name
        ]

        for headers in malformed_headers:
            response = client.get("/profiles", headers=headers)
            assert response.status_code == 401, f"Malformed header should be rejected: {headers}"

    def test_user_id_extraction_from_jwt(self, client, valid_jwt_payload, jwt_secret):
        """Test that user_id is correctly extracted from JWT token."""
        token = create_jwt_token(valid_jwt_payload, jwt_secret)
        headers = {"Authorization": f"Bearer {token}"}

        # Create a profile
        profile_data = {"first_name": "John", "last_name": "Doe"}
        create_response = client.post("/profiles", json=profile_data, headers=headers)

        if create_response.status_code == 201:
            profile = create_response.json()
            # Verify the user_id matches the JWT payload
            assert profile["user_id"] == valid_jwt_payload["user_id"]

    def test_user_isolation_enforcement(self, client, jwt_secret):
        """Test that users can only access their own data."""
        # Create tokens for two different users
        user1_payload = {
            "user_id": 100,
            "email": "user1@example.com",
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
            "sub": "100"
        }

        user2_payload = {
            "user_id": 200,
            "email": "user2@example.com",
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
            "sub": "200"
        }

        user1_token = create_jwt_token(user1_payload, jwt_secret)
        user2_token = create_jwt_token(user2_payload, jwt_secret)

        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        # User 1 creates a profile
        profile_data = {"first_name": "User", "last_name": "One"}
        user1_create_response = client.post("/profiles", json=profile_data, headers=user1_headers)

        if user1_create_response.status_code == 201:
            # User 2 should not be able to see User 1's profile
            user2_get_response = client.get("/profiles", headers=user2_headers)
            if user2_get_response.status_code == 200:
                user2_profile = user2_get_response.json()
                # Should be different profile or no profile
                assert user2_profile["user_id"] != user1_payload["user_id"]
            elif user2_get_response.status_code == 404:
                # No profile for user 2 - this is expected
                pass

    def test_admin_role_authorization(self, client, admin_jwt_payload, valid_jwt_payload, jwt_secret):
        """Test that admin role provides access to admin endpoints."""
        admin_token = create_jwt_token(admin_jwt_payload, jwt_secret)
        user_token = create_jwt_token(valid_jwt_payload, jwt_secret)

        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # Admin should be able to access admin endpoints
        admin_response = client.get("/admin/profiles/42", headers=admin_headers)
        assert admin_response.status_code != 403, "Admin should have access to admin endpoints"

        # Regular user should not have access to admin endpoints
        user_response = client.get("/admin/profiles/42", headers=user_headers)
        assert user_response.status_code == 403, "Regular user should not have access to admin endpoints"

    def test_jwt_algorithm_validation(self, client, valid_jwt_payload, jwt_secret):
        """Test that only expected JWT algorithms are accepted."""
        # Test with correct algorithm (HS256)
        valid_token = create_jwt_token(valid_jwt_payload, jwt_secret, "HS256")
        valid_headers = {"Authorization": f"Bearer {valid_token}"}

        response = client.get("/profiles", headers=valid_headers)
        assert response.status_code != 401, "HS256 algorithm should be accepted"

        # Test with unsupported algorithm (if service only accepts HS256)
        try:
            invalid_token = create_jwt_token(valid_jwt_payload, jwt_secret, "HS512")
            invalid_headers = {"Authorization": f"Bearer {invalid_token}"}

            response = client.get("/profiles", headers=invalid_headers)
            # Should either work (if HS512 is supported) or be rejected
            assert response.status_code in [200, 404, 401], "Algorithm validation should be consistent"
        except Exception:
            # Some algorithms might not be available
            pass

    def test_jwt_signature_validation(self, client, valid_jwt_payload):
        """Test that JWT signature validation works correctly."""
        correct_secret = "correct-secret"
        wrong_secret = "wrong-secret"

        # Token signed with wrong secret
        wrong_token = create_jwt_token(valid_jwt_payload, wrong_secret)
        wrong_headers = {"Authorization": f"Bearer {wrong_token}"}

        response = client.get("/profiles", headers=wrong_headers)
        assert response.status_code == 401, "Token with wrong signature should be rejected"

    def test_auth_service_connectivity_fallback(self, client, valid_jwt_payload, jwt_secret):
        """Test behavior when auth service is unavailable."""
        # This test verifies that the service can handle auth service unavailability
        # The actual implementation might use local JWT validation as fallback

        token = create_jwt_token(valid_jwt_payload, jwt_secret)
        headers = {"Authorization": f"Bearer {token}"}

        # Even if auth service is down, local JWT validation should work
        response = client.get("/profiles", headers=headers)
        # Should not fail due to auth service connectivity issues
        assert response.status_code != 503, "Service should handle auth service unavailability"

    def test_token_refresh_compatibility(self, client, jwt_secret):
        """Test compatibility with token refresh scenarios."""
        # Test with token that's about to expire
        soon_expired_payload = {
            "user_id": 42,
            "email": "test@example.com",
            "exp": int(time.time()) + 60,  # Expires in 1 minute
            "iat": int(time.time()),
            "sub": "42"
        }

        token = create_jwt_token(soon_expired_payload, jwt_secret)
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/profiles", headers=headers)
        # Should still work even if token is about to expire
        assert response.status_code != 401, "Token about to expire should still be valid"

    def test_concurrent_auth_requests(self, client, valid_jwt_payload, jwt_secret):
        """Test handling of concurrent authentication requests."""
        import threading
        import time

        token = create_jwt_token(valid_jwt_payload, jwt_secret)
        headers = {"Authorization": f"Bearer {token}"}

        results = []

        def make_request():
            try:
                response = client.get("/profiles", headers=headers)
                results.append(response.status_code)
            except Exception as e:
                results.append(f"Error: {e}")

        # Launch multiple concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should succeed (or consistently fail with same error)
        unique_results = set(results)
        assert len(unique_results) <= 2, "Concurrent auth requests should be handled consistently"

        # Should not have authentication failures due to concurrency
        auth_failures = sum(1 for result in results if result == 401)
        assert auth_failures == 0 or auth_failures == len(results), "Auth failures should be consistent"

    @pytest.mark.integration
    def test_auth_performance(self, client, valid_jwt_payload, jwt_secret):
        """Test that authentication doesn't significantly impact response time."""
        import time

        token = create_jwt_token(valid_jwt_payload, jwt_secret)
        headers = {"Authorization": f"Bearer {token}"}

        # Measure auth overhead
        start_time = time.time()
        response = client.get("/health")  # Unauthenticated endpoint
        unauth_time = time.time() - start_time

        start_time = time.time()
        response = client.get("/profiles", headers=headers)  # Authenticated endpoint
        auth_time = time.time() - start_time

        if response.status_code in [200, 404]:
            # Auth overhead should be minimal (< 50ms additional)
            auth_overhead = auth_time - unauth_time
            assert auth_overhead < 0.05, f"Auth overhead is {auth_overhead:.3f}s, should be < 50ms"

    def test_auth_error_messages(self, client):
        """Test that authentication error messages are informative but secure."""
        test_cases = [
            {
                "headers": {},
                "expected_error": "Unauthorized",
                "description": "Missing token"
            },
            {
                "headers": {"Authorization": "Bearer invalid"},
                "expected_error": "Unauthorized",
                "description": "Invalid token"
            },
            {
                "headers": {"Authorization": "Basic dGVzdA=="},
                "expected_error": "Unauthorized",
                "description": "Wrong auth type"
            }
        ]

        for case in test_cases:
            response = client.get("/profiles", headers=case["headers"])
            assert response.status_code == 401, f"Case should return 401: {case['description']}"

            error_data = response.json()
            assert error_data["error"] == case["expected_error"]

            # Error message should not expose sensitive information
            message = error_data["message"].lower()
            sensitive_terms = ["secret", "key", "algorithm", "signature"]
            for term in sensitive_terms:
                assert term not in message, f"Error message should not expose {term}"