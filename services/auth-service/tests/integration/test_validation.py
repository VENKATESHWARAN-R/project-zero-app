"""
Integration test for input validation and error handling.
Tests Story 6 from quickstart.md: Input Validation.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestInputValidation:
    """Test input validation and error handling integration."""

    def test_input_validation_flow_missing_fields(self):
        """Test input validation for missing required fields."""
        # This test should fail initially (TDD)
        # Story 6: Input Validation

        # Test missing password field
        login_data = {"email": "test@example.com"}
        response = client.post("/auth/login", json=login_data)

        # Success Criteria from quickstart.md:
        # ✅ Returns 422 for validation errors
        assert response.status_code == 422

        # ✅ Provides clear error messages
        data = response.json()
        assert "detail" in data

        # Test missing email field
        login_data = {"password": "SecurePass123"}
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 422

    def test_input_validation_email_format(self):
        """Test email format validation."""
        # Success Criteria from quickstart.md:
        # ✅ Returns 422 for validation errors

        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user..name@example.com",
            "user name@example.com",
            "user@.com",
            "user@com",
            "",
            " ",
            "user@example.",
            "user@-example.com"
        ]

        for invalid_email in invalid_emails:
            response = client.post("/auth/login", json={
                "email": invalid_email,
                "password": "SecurePass123"
            })
            assert response.status_code == 422, f"Email '{invalid_email}' should be invalid"

    def test_input_validation_email_format_valid(self):
        """Test that valid email formats are accepted."""
        valid_emails = [
            "user@example.com",
            "test.email@domain.org",
            "user123@test-domain.co.uk",
            "firstname.lastname@subdomain.example.com",
            "user+tag@example.com"
        ]

        for valid_email in valid_emails:
            response = client.post("/auth/login", json={
                "email": valid_email,
                "password": "SecurePass123"
            })
            # Should not fail validation (might fail auth with 401, but not 422)
            assert response.status_code != 422, f"Email '{valid_email}' should be valid"

    def test_input_validation_password_requirements(self):
        """Test password validation requirements."""
        # Test passwords that don't meet requirements

        weak_passwords = [
            "short",           # Too short
            "1234567",         # Too short, only numbers
            "password",        # Only lowercase
            "PASSWORD",        # Only uppercase
            "Pass123",         # Under 8 characters
            ""                 # Empty
        ]

        for weak_password in weak_passwords:
            response = client.post("/auth/login", json={
                "email": "test@example.com",
                "password": weak_password
            })
            # Should fail validation
            assert response.status_code == 422, f"Password '{weak_password}' should be invalid"

    def test_input_validation_password_requirements_valid(self):
        """Test that valid passwords are accepted."""
        valid_passwords = [
            "SecurePass123",
            "MyPassword1",
            "Complex!Pass123",
            "ValidPass99",
            "StrongPassword2024"
        ]

        for valid_password in valid_passwords:
            response = client.post("/auth/login", json={
                "email": "test@example.com",
                "password": valid_password
            })
            # Should not fail validation (might fail auth with 401, but not 422)
            assert response.status_code != 422, f"Password '{valid_password}' should be valid"

    def test_input_validation_malformed_json(self):
        """Test handling of malformed JSON requests."""
        # Success Criteria from quickstart.md:
        # ✅ Rejects malformed JSON

        # Send malformed JSON
        response = client.post(
            "/auth/login",
            data='{"email": "test@example.com", "password":}',  # Missing value
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

        # Send non-JSON data with JSON content type
        response = client.post(
            "/auth/login",
            data="not json data",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_input_validation_wrong_content_type(self):
        """Test handling of wrong content types."""
        # Form data instead of JSON
        response = client.post(
            "/auth/login",
            data={"email": "test@example.com", "password": "SecurePass123"}
        )
        # Should require JSON content type
        assert response.status_code in [422, 415]

        # Plain text instead of JSON
        response = client.post(
            "/auth/login",
            data="email=test@example.com&password=SecurePass123",
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code in [422, 415]

    def test_input_validation_empty_request_body(self):
        """Test handling of empty request body."""
        # Success Criteria from quickstart.md:
        # ✅ Handles missing required fields

        # Completely empty body
        response = client.post("/auth/login", json={})
        assert response.status_code == 422

        # Null body
        response = client.post(
            "/auth/login",
            data="",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_input_validation_extra_fields(self):
        """Test handling of extra/unexpected fields."""
        # Request with extra fields
        login_data = {
            "email": "test@example.com",
            "password": "SecurePass123",
            "extra_field": "should_be_ignored",
            "another_field": 123
        }

        response = client.post("/auth/login", json=login_data)

        # Should either ignore extra fields or reject them
        # Pydantic typically ignores extra fields by default
        assert response.status_code in [200, 401, 422]

    def test_input_validation_field_types(self):
        """Test validation of field types."""
        # Wrong type for email (number instead of string)
        response = client.post("/auth/login", json={
            "email": 12345,
            "password": "SecurePass123"
        })
        assert response.status_code == 422

        # Wrong type for password (array instead of string)
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": ["SecurePass123"]
        })
        assert response.status_code == 422

        # Boolean values
        response = client.post("/auth/login", json={
            "email": True,
            "password": False
        })
        assert response.status_code == 422

    def test_input_validation_null_values(self):
        """Test handling of null values."""
        # Null email
        response = client.post("/auth/login", json={
            "email": None,
            "password": "SecurePass123"
        })
        assert response.status_code == 422

        # Null password
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": None
        })
        assert response.status_code == 422

        # Both null
        response = client.post("/auth/login", json={
            "email": None,
            "password": None
        })
        assert response.status_code == 422

    def test_input_validation_whitespace_handling(self):
        """Test handling of whitespace in inputs."""
        # Leading/trailing whitespace in email
        response = client.post("/auth/login", json={
            "email": "  test@example.com  ",
            "password": "SecurePass123"
        })
        # Should either trim whitespace or reject
        assert response.status_code in [200, 401, 422]

        # Whitespace in password (should be preserved)
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "  SecurePass123  "
        })
        # Should accept (whitespace is valid in passwords)
        assert response.status_code in [200, 401]

    def test_input_validation_very_long_inputs(self):
        """Test handling of very long inputs."""
        # Very long email
        long_email = "a" * 1000 + "@example.com"
        response = client.post("/auth/login", json={
            "email": long_email,
            "password": "SecurePass123"
        })
        # Should either accept or reject based on length limits
        assert response.status_code in [200, 401, 422]

        # Very long password
        long_password = "SecurePass" + "a" * 1000
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": long_password
        })
        # Should either accept or reject based on length limits
        assert response.status_code in [200, 401, 422]

    def test_input_validation_special_characters(self):
        """Test handling of special characters."""
        # Email with special characters
        special_emails = [
            "test+tag@example.com",
            "test.name@example.com",
            "test_name@example.com",
            "test-name@example.com"
        ]

        for email in special_emails:
            response = client.post("/auth/login", json={
                "email": email,
                "password": "SecurePass123"
            })
            # These should be valid email formats
            assert response.status_code != 422

        # Password with special characters
        special_passwords = [
            "SecurePass123!",
            "Pass@word123",
            "My#Password$",
            "Test%Pass^&*()"
        ]

        for password in special_passwords:
            response = client.post("/auth/login", json={
                "email": "test@example.com",
                "password": password
            })
            # Should accept special characters in passwords
            assert response.status_code != 422

    def test_input_validation_unicode_handling(self):
        """Test handling of Unicode characters."""
        # Unicode in email (should be handled properly)
        unicode_email = "tëst@example.com"
        response = client.post("/auth/login", json={
            "email": unicode_email,
            "password": "SecurePass123"
        })
        # Should handle Unicode properly
        assert response.status_code in [200, 401, 422]

        # Unicode in password
        unicode_password = "SecurePass123ñ"
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": unicode_password
        })
        # Should handle Unicode in passwords
        assert response.status_code in [200, 401]

    def test_input_validation_error_message_quality(self):
        """Test quality of validation error messages."""
        # Missing email field
        response = client.post("/auth/login", json={"password": "SecurePass123"})
        assert response.status_code == 422

        data = response.json()
        # Should have detailed error information
        assert "detail" in data

        # Error message should be helpful
        if isinstance(data["detail"], list):
            # FastAPI validation error format
            assert len(data["detail"]) > 0
        elif isinstance(data["detail"], str):
            # Simple string error
            assert len(data["detail"]) > 0

    def test_input_validation_refresh_endpoint(self):
        """Test input validation for refresh endpoint."""
        # Missing refresh token
        response = client.post("/auth/refresh", json={})
        assert response.status_code == 422

        # Wrong type for refresh token
        response = client.post("/auth/refresh", json={"refresh_token": 123})
        assert response.status_code == 422

        # Null refresh token
        response = client.post("/auth/refresh", json={"refresh_token": None})
        assert response.status_code == 422

    def test_input_validation_logout_endpoint(self):
        """Test input validation for logout endpoint."""
        # Missing refresh token
        response = client.post("/auth/logout", json={})
        assert response.status_code == 422

        # Wrong type for refresh token
        response = client.post("/auth/logout", json={"refresh_token": 123})
        assert response.status_code == 422

        # Empty string refresh token
        response = client.post("/auth/logout", json={"refresh_token": ""})
        assert response.status_code in [400, 422]

    def test_input_validation_verify_endpoint(self):
        """Test input validation for verify endpoint."""
        # Missing Authorization header
        response = client.get("/auth/verify")
        assert response.status_code == 401

        # Malformed Authorization header
        response = client.get("/auth/verify", headers={"Authorization": "InvalidFormat"})
        assert response.status_code == 401

        # Empty Authorization header
        response = client.get("/auth/verify", headers={"Authorization": ""})
        assert response.status_code == 401

    def test_input_validation_cross_endpoint_consistency(self):
        """Test that validation is consistent across endpoints."""
        # All endpoints should handle malformed JSON consistently
        endpoints = [
            ("/auth/login", "POST"),
            ("/auth/logout", "POST"),
            ("/auth/refresh", "POST")
        ]

        for endpoint, method in endpoints:
            if method == "POST":
                response = client.post(
                    endpoint,
                    data='{"invalid": json}',
                    headers={"Content-Type": "application/json"}
                )
                # All should return 422 for malformed JSON
                assert response.status_code == 422

    def test_input_validation_security_considerations(self):
        """Test security aspects of input validation."""
        # SQL injection attempt in email
        sql_injection_email = "'; DROP TABLE users; --@example.com"
        response = client.post("/auth/login", json={
            "email": sql_injection_email,
            "password": "SecurePass123"
        })
        # Should either be rejected as invalid email or handled safely
        assert response.status_code in [200, 401, 422]

        # XSS attempt in inputs
        xss_email = "<script>alert('xss')</script>@example.com"
        response = client.post("/auth/login", json={
            "email": xss_email,
            "password": "SecurePass123"
        })
        # Should handle without executing scripts
        assert response.status_code in [200, 401, 422]

    def test_input_validation_performance_with_large_payloads(self):
        """Test validation performance with large payloads."""
        import time

        # Large but valid payload
        large_payload = {
            "email": "test@example.com",
            "password": "SecurePass123",
            "extra_data": "x" * 10000  # Large extra field
        }

        start_time = time.time()
        response = client.post("/auth/login", json=large_payload)
        end_time = time.time()

        response_time = end_time - start_time

        # Should handle large payloads efficiently
        assert response_time < 1.0
        # Should either ignore extra data or reject it
        assert response.status_code in [200, 401, 422]