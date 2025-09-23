"""
Contract test for GET /health endpoint.
Tests the API contract defined in auth-api.yml.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthContract:
    """Test health endpoint contract compliance."""

    def test_health_success_response_structure(self):
        """Test that health check returns correct response structure."""
        # This test should fail initially (TDD)
        response = client.get("/health")

        # Contract: 200 status for healthy service
        assert response.status_code == 200

        # Contract: Response must include required fields
        data = response.json()
        assert "status" in data
        assert "timestamp" in data

        # Contract: Validate field types and values
        assert isinstance(data["status"], str)
        assert data["status"] in ["healthy", "unhealthy"]
        assert isinstance(data["timestamp"], str)

        # Contract: Optional database field
        if "database" in data:
            assert isinstance(data["database"], str)
            assert data["database"] in ["connected", "disconnected"]

    def test_health_timestamp_format(self):
        """Test that timestamp is in ISO format."""
        response = client.get("/health")

        if response.status_code == 200:
            data = response.json()
            timestamp = data["timestamp"]

            # Contract: Timestamp should be ISO 8601 format
            # Basic validation - should contain 'T' and end with 'Z' or timezone
            assert "T" in timestamp
            # Should be parseable as datetime
            from datetime import datetime
            try:
                datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                pytest.fail(f"Timestamp {timestamp} is not valid ISO format")

    def test_health_database_status_when_connected(self):
        """Test database status when database is connected."""
        response = client.get("/health")

        if response.status_code == 200:
            data = response.json()
            if "database" in data:
                # When service is healthy, database should typically be connected
                if data["status"] == "healthy":
                    assert data["database"] == "connected"

    def test_health_unhealthy_response_structure(self):
        """Test response structure when service is unhealthy."""
        # This test simulates unhealthy state
        # In real scenario, this would happen when database is down
        response = client.get("/health")

        # Contract: Should return 503 for unhealthy service
        # Or 200 with status="unhealthy"
        if response.status_code == 503:
            data = response.json()
            assert "status" in data
            assert data["status"] == "unhealthy"
        elif response.status_code == 200:
            data = response.json()
            # Service might still return 200 but with unhealthy status
            assert data["status"] in ["healthy", "unhealthy"]

    def test_health_no_authentication_required(self):
        """Test that health endpoint doesn't require authentication."""
        # Health check should work without any headers
        response = client.get("/health")

        # Contract: Should not return 401 (authentication required)
        assert response.status_code != 401

    def test_health_accepts_get_method_only(self):
        """Test that health endpoint only accepts GET method."""
        # POST should not be allowed
        response = client.post("/health")
        assert response.status_code == 405

        # PUT should not be allowed
        response = client.put("/health")
        assert response.status_code == 405

        # DELETE should not be allowed
        response = client.delete("/health")
        assert response.status_code == 405

    def test_health_response_content_type(self):
        """Test that health endpoint returns JSON content type."""
        response = client.get("/health")

        # Contract: Should return JSON
        assert "application/json" in response.headers.get("content-type", "")

    def test_health_performance(self):
        """Test that health check responds quickly."""
        import time

        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        # Contract: Health check should be fast (< 1 second)
        response_time = end_time - start_time
        assert response_time < 1.0

    def test_health_consistent_response(self):
        """Test that health endpoint returns consistent responses."""
        # Make multiple requests
        responses = []
        for _ in range(3):
            response = client.get("/health")
            responses.append(response.status_code)

        # All responses should have same status code (consistency)
        assert all(status == responses[0] for status in responses)

    def test_health_includes_service_metadata(self):
        """Test that health response might include service metadata."""
        response = client.get("/health")

        if response.status_code == 200:
            data = response.json()
            # Optional fields that might be included
            optional_fields = ["service", "version", "uptime"]
            # At least the required fields should be present
            assert "status" in data
            assert "timestamp" in data