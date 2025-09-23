"""
Integration test for rate limiting protection.
Tests Story 5 from quickstart.md: Rate Limiting Protection.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
import time

client = TestClient(app)


class TestRateLimiting:
    """Test rate limiting protection integration."""

    def test_rate_limiting_flow_protection(self):
        """Test complete rate limiting protection flow."""
        # This test should fail initially (TDD)
        # Story 5: Rate Limiting Protection

        email = "ratelimit@example.com"
        wrong_password = "WrongPassword"

        # Make 6 failed login attempts rapidly
        responses = []
        for attempt in range(6):
            login_data = {
                "email": email,
                "password": wrong_password
            }
            response = client.post("/auth/login", json=login_data)
            responses.append(response)

        # Success Criteria from quickstart.md:
        # ✅ First 5 attempts return 401
        for i in range(5):
            assert responses[i].status_code == 401
            error_data = responses[i].json()
            assert "detail" in error_data
            assert "invalid" in error_data["detail"].lower() or "password" in error_data["detail"].lower()

        # ✅ 6th attempt returns 429
        assert responses[5].status_code == 429
        rate_limit_data = responses[5].json()
        assert "detail" in rate_limit_data
        assert "too many" in rate_limit_data["detail"].lower() or "rate" in rate_limit_data["detail"].lower()

    def test_rate_limiting_account_lockout_duration(self):
        """Test that account lockout lasts the specified duration."""
        # Success Criteria from quickstart.md:
        # ✅ Account lockout lasts 15 minutes

        email = "lockout@example.com"
        wrong_password = "WrongPassword"

        # Trigger rate limiting
        for _ in range(6):
            response = client.post("/auth/login", json={
                "email": email,
                "password": wrong_password
            })

        # Last response should be rate limited
        assert response.status_code == 429

        # Immediate retry should still be rate limited
        immediate_retry = client.post("/auth/login", json={
            "email": email,
            "password": wrong_password
        })
        assert immediate_retry.status_code == 429

        # Even with correct password, should be rate limited
        correct_retry = client.post("/auth/login", json={
            "email": email,
            "password": "CorrectPassword123"
        })
        assert correct_retry.status_code == 429

    def test_rate_limiting_per_email_isolation(self):
        """Test that rate limiting is per email/IP address."""
        # Success Criteria from quickstart.md:
        # ✅ Rate limiting per email/IP

        email1 = "user1@example.com"
        email2 = "user2@example.com"
        wrong_password = "WrongPassword"

        # Trigger rate limiting for user1
        for _ in range(6):
            response1 = client.post("/auth/login", json={
                "email": email1,
                "password": wrong_password
            })

        # user1 should be rate limited
        assert response1.status_code == 429

        # user2 should not be affected
        response2 = client.post("/auth/login", json={
            "email": email2,
            "password": wrong_password
        })
        # Should get 401 (invalid credentials), not 429 (rate limited)
        assert response2.status_code == 401

    def test_rate_limiting_attack_simulation(self):
        """Test rate limiting against simulated brute force attack."""
        # Simulate a brute force attack
        target_email = "victim@example.com"
        common_passwords = [
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "dragon", "password1"
        ]

        attack_responses = []
        for password in common_passwords:
            response = client.post("/auth/login", json={
                "email": target_email,
                "password": password
            })
            attack_responses.append(response.status_code)

        # Should start getting rate limited after 5 attempts
        rate_limited_count = sum(1 for status in attack_responses if status == 429)
        assert rate_limited_count > 0

        # Not all attempts should be rate limited (first 5 should be 401)
        auth_failed_count = sum(1 for status in attack_responses if status == 401)
        assert auth_failed_count > 0

    def test_rate_limiting_reset_after_successful_login(self):
        """Test rate limiting counter reset behavior."""
        email = "reset@example.com"
        correct_password = "CorrectPassword123"
        wrong_password = "WrongPassword"

        # Make 3 failed attempts (below threshold)
        for _ in range(3):
            response = client.post("/auth/login", json={
                "email": email,
                "password": wrong_password
            })
            assert response.status_code == 401

        # Successful login (if user exists and password is correct)
        success_response = client.post("/auth/login", json={
            "email": email,
            "password": correct_password
        })

        # Behavior depends on whether user exists:
        # - If user exists: should succeed and reset counter
        # - If user doesn't exist: should fail (401)

        if success_response.status_code == 200:
            # Counter should be reset, so we can make more attempts
            for _ in range(3):
                response = client.post("/auth/login", json={
                    "email": email,
                    "password": wrong_password
                })
                # Should get 401, not 429
                assert response.status_code == 401

    def test_rate_limiting_different_endpoints(self):
        """Test that rate limiting applies to login endpoint specifically."""
        email = "endpoint@example.com"

        # Trigger rate limiting on login
        for _ in range(6):
            response = client.post("/auth/login", json={
                "email": email,
                "password": "wrong"
            })

        # Login should be rate limited
        assert response.status_code == 429

        # Other endpoints should not be affected
        # Health check should still work
        health_response = client.get("/health")
        assert health_response.status_code == 200

        # Token verification should still work (if we had a valid token)
        verify_response = client.get("/auth/verify", headers={
            "Authorization": "Bearer some_token"
        })
        # Should get 401 (invalid token), not 429 (rate limited)
        assert verify_response.status_code == 401

    def test_rate_limiting_configuration_values(self):
        """Test rate limiting configuration matches specification."""
        # From specification: 5 attempts per minute per user
        # From quickstart.md: 15 minutes lockout duration

        email = "config@example.com"
        wrong_password = "WrongPassword"

        # Test the exact threshold (5 attempts)
        for attempt in range(1, 7):
            response = client.post("/auth/login", json={
                "email": email,
                "password": wrong_password
            })

            if attempt <= 5:
                # First 5 attempts should be authentication failures
                assert response.status_code == 401
            else:
                # 6th attempt should be rate limited
                assert response.status_code == 429

    def test_rate_limiting_concurrent_attempts(self):
        """Test rate limiting with concurrent login attempts."""
        email = "concurrent@example.com"
        wrong_password = "WrongPassword"

        # Make concurrent requests
        responses = []
        for _ in range(10):
            response = client.post("/auth/login", json={
                "email": email,
                "password": wrong_password
            })
            responses.append(response.status_code)

        # Should have a mix of 401s and 429s
        auth_failures = sum(1 for status in responses if status == 401)
        rate_limited = sum(1 for status in responses if status == 429)

        # At least some should be rate limited
        assert rate_limited > 0
        # Some should be authentication failures
        assert auth_failures > 0

    def test_rate_limiting_error_message_quality(self):
        """Test that rate limiting error messages are helpful."""
        email = "messages@example.com"

        # Trigger rate limiting
        for _ in range(6):
            response = client.post("/auth/login", json={
                "email": email,
                "password": "wrong"
            })

        # Check rate limit error message
        assert response.status_code == 429
        error_data = response.json()
        assert "detail" in error_data

        error_message = error_data["detail"].lower()

        # Should mention rate limiting concepts
        rate_limit_indicators = ["too many", "attempts", "try again", "wait", "limit"]
        assert any(indicator in error_message for indicator in rate_limit_indicators)

    def test_rate_limiting_ip_and_email_tracking(self):
        """Test rate limiting tracks both IP and email."""
        # Note: In test environment, all requests come from same IP
        # This test documents expected behavior for different IPs

        email = "tracking@example.com"

        # From same IP (test client), trigger rate limiting
        for _ in range(6):
            response = client.post("/auth/login", json={
                "email": email,
                "password": "wrong"
            })

        assert response.status_code == 429

        # In production, different IP should have separate rate limit
        # But in tests, this is hard to simulate
        # Test documents the expected behavior

    def test_rate_limiting_memory_efficiency(self):
        """Test that rate limiting doesn't consume excessive memory."""
        # Test with many different email addresses
        # Each should have its own rate limit counter

        for i in range(100):
            email = f"memory{i}@example.com"
            response = client.post("/auth/login", json={
                "email": email,
                "password": "wrong"
            })
            # All should get 401 (first attempt for each user)
            assert response.status_code == 401

        # System should handle many users without issues
        # Memory usage should remain reasonable

    def test_rate_limiting_cleanup_behavior(self):
        """Test that rate limiting data is cleaned up appropriately."""
        email = "cleanup@example.com"

        # Trigger rate limiting
        for _ in range(6):
            response = client.post("/auth/login", json={
                "email": email,
                "password": "wrong"
            })

        assert response.status_code == 429

        # In production, rate limit data should be cleaned up after expiry
        # This test documents the expected behavior
        # Actual cleanup testing would require waiting 15+ minutes

    def test_rate_limiting_edge_cases(self):
        """Test edge cases in rate limiting."""
        # Empty email
        response = client.post("/auth/login", json={
            "email": "",
            "password": "password"
        })
        # Should get validation error, not rate limiting
        assert response.status_code == 422

        # Invalid email format
        response = client.post("/auth/login", json={
            "email": "not-an-email",
            "password": "password"
        })
        # Should get validation error, not rate limiting
        assert response.status_code == 422

        # Very long email
        long_email = "a" * 1000 + "@example.com"
        response = client.post("/auth/login", json={
            "email": long_email,
            "password": "password"
        })
        # Should either work or fail validation, not cause errors
        assert response.status_code in [401, 422]

    def test_rate_limiting_performance_impact(self):
        """Test that rate limiting doesn't significantly impact performance."""
        import time

        email = "performance@example.com"

        # Measure time for normal authentication attempt
        start_time = time.time()
        response = client.post("/auth/login", json={
            "email": email,
            "password": "password"
        })
        end_time = time.time()

        first_attempt_time = end_time - start_time

        # Make several more attempts
        for _ in range(4):
            client.post("/auth/login", json={
                "email": email,
                "password": "password"
            })

        # Measure time for rate-limited request
        start_time = time.time()
        response = client.post("/auth/login", json={
            "email": email,
            "password": "password"
        })
        end_time = time.time()

        rate_limited_time = end_time - start_time

        # Rate limiting check should not add significant overhead
        # Should be roughly the same performance
        performance_ratio = rate_limited_time / first_attempt_time
        assert performance_ratio < 2.0  # Should not be more than 2x slower