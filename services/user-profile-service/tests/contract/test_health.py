"""Contract tests for health endpoints.

These tests verify that the health endpoints conform to the OpenAPI specification
and return the expected response schemas.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from typing import Literal


class HealthResponse(BaseModel):
    """Expected health response schema from OpenAPI spec."""
    status: Literal["healthy", "unhealthy"]
    service: str
    version: str
    timestamp: str
    database: Literal["connected", "disconnected"]


class ReadinessResponse(BaseModel):
    """Expected readiness response schema from OpenAPI spec."""
    status: Literal["ready", "not_ready"]
    service: str
    checks: dict[str, Literal["ready", "not_ready"]]
    timestamp: str


@pytest.fixture
def client():
    """Test client fixture - will be implemented once FastAPI app exists."""
    # This will fail initially as the app doesn't exist yet
    from main import app
    return TestClient(app)


class TestHealthEndpoints:
    """Contract tests for health check endpoints."""

    def test_health_endpoint_exists(self, client):
        """Test that GET /health endpoint exists and is accessible."""
        response = client.get("/health")
        assert response.status_code in [200, 503], "Health endpoint should return 200 or 503"

    def test_health_response_schema(self, client):
        """Test that /health returns valid HealthResponse schema."""
        response = client.get("/health")

        # Validate response can be parsed as HealthResponse
        health_data = HealthResponse.model_validate(response.json())

        # Verify required fields are present and correct
        assert health_data.service == "user-profile-service"
        assert health_data.version == "1.0.0"
        assert health_data.status in ["healthy", "unhealthy"]
        assert health_data.database in ["connected", "disconnected"]
        assert health_data.timestamp is not None

    def test_health_response_content_type(self, client):
        """Test that /health returns application/json content type."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

    def test_readiness_endpoint_exists(self, client):
        """Test that GET /health/ready endpoint exists and is accessible."""
        response = client.get("/health/ready")
        assert response.status_code in [200, 503], "Readiness endpoint should return 200 or 503"

    def test_readiness_response_schema(self, client):
        """Test that /health/ready returns valid ReadinessResponse schema."""
        response = client.get("/health/ready")

        # Validate response can be parsed as ReadinessResponse
        readiness_data = ReadinessResponse.model_validate(response.json())

        # Verify required fields are present and correct
        assert readiness_data.service == "user-profile-service"
        assert readiness_data.status in ["ready", "not_ready"]
        assert "database" in readiness_data.checks
        assert "auth_service" in readiness_data.checks
        assert readiness_data.timestamp is not None

    def test_readiness_response_content_type(self, client):
        """Test that /health/ready returns application/json content type."""
        response = client.get("/health/ready")
        assert response.headers["content-type"] == "application/json"

    def test_health_endpoint_no_auth_required(self, client):
        """Test that health endpoints don't require authentication."""
        # Should work without any Authorization header
        response = client.get("/health")
        assert response.status_code != 401, "Health endpoint should not require authentication"

        response = client.get("/health/ready")
        assert response.status_code != 401, "Readiness endpoint should not require authentication"

    def test_health_database_check_reflects_status(self, client):
        """Test that health endpoint database check reflects actual database status."""
        response = client.get("/health")
        health_data = HealthResponse.model_validate(response.json())

        # If database is connected, overall status should be healthy
        if health_data.database == "connected":
            assert health_data.status == "healthy"

        # If database is disconnected, overall status should be unhealthy
        if health_data.database == "disconnected":
            assert health_data.status == "unhealthy"

    def test_readiness_dependency_checks(self, client):
        """Test that readiness endpoint performs dependency checks."""
        response = client.get("/health/ready")
        readiness_data = ReadinessResponse.model_validate(response.json())

        # Verify all required service checks are performed
        required_checks = ["database", "auth_service"]
        for check in required_checks:
            assert check in readiness_data.checks
            assert readiness_data.checks[check] in ["ready", "not_ready"]

        # If all checks are ready, overall status should be ready
        all_ready = all(
            status == "ready"
            for status in readiness_data.checks.values()
        )
        if all_ready:
            assert readiness_data.status == "ready"

    @pytest.mark.integration
    def test_health_endpoint_performance(self, client):
        """Test that health endpoints respond quickly (< 1 second)."""
        import time

        # Test health endpoint performance
        start_time = time.time()
        response = client.get("/health")
        health_duration = time.time() - start_time

        assert health_duration < 1.0, f"Health endpoint took {health_duration:.2f}s, should be < 1s"
        assert response.status_code in [200, 503]

        # Test readiness endpoint performance
        start_time = time.time()
        response = client.get("/health/ready")
        readiness_duration = time.time() - start_time

        assert readiness_duration < 1.0, f"Readiness endpoint took {readiness_duration:.2f}s, should be < 1s"
        assert response.status_code in [200, 503]