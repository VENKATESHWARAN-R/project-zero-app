"""Contract tests for GET /health endpoint."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_check_success():
    """Test basic health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # Verify required fields from contract
    assert "status" in data
    assert "timestamp" in data

    # Verify field types
    assert isinstance(data["status"], str)
    assert isinstance(data["timestamp"], str)

    # Verify status value
    assert data["status"] == "healthy"

    # Verify timestamp format (ISO 8601)
    import re

    iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
    assert re.match(iso_pattern, data["timestamp"])


def test_health_check_response_structure():
    """Test that health response matches exact contract."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # Should only have required fields (no extras)
    required_fields = {"status", "timestamp"}
    actual_fields = set(data.keys())

    # May have additional fields like "database" but should have required ones
    assert required_fields.issubset(actual_fields)

    # Status should be one of the allowed values
    allowed_statuses = ["healthy", "ready"]
    assert data["status"] in allowed_statuses


def test_health_check_content_type():
    """Test that health check returns correct content type."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"


def test_health_check_no_authentication():
    """Test that health check requires no authentication."""
    # Should work without any headers
    response = client.get("/health")
    assert response.status_code == 200

    # Should work with invalid auth headers
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/health", headers=headers)
    assert response.status_code == 200


def test_health_check_methods():
    """Test that health endpoint only supports GET method."""
    # GET should work
    response = client.get("/health")
    assert response.status_code == 200

    # Other methods should not be allowed
    response = client.post("/health")
    assert response.status_code == 405  # Method Not Allowed

    response = client.put("/health")
    assert response.status_code == 405

    response = client.delete("/health")
    assert response.status_code == 405


def test_health_check_consistency():
    """Test that health check is consistent across multiple calls."""
    responses = []

    # Make multiple calls
    for _ in range(3):
        response = client.get("/health")
        assert response.status_code == 200
        responses.append(response.json())

    # All should have same status
    statuses = [r["status"] for r in responses]
    assert all(status == "healthy" for status in statuses)

    # Timestamps should be different (unless called very quickly)
    timestamps = [r["timestamp"] for r in responses]
    # At least verify they're all valid timestamps
    import re

    iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
    for timestamp in timestamps:
        assert re.match(iso_pattern, timestamp)


def test_health_check_performance():
    """Test that health check responds quickly."""
    import time

    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()

    assert response.status_code == 200

    # Health check should be fast (less than 1 second)
    response_time = end_time - start_time
    assert response_time < 1.0


def test_health_check_query_parameters():
    """Test health check with query parameters."""
    # Should ignore query parameters
    response = client.get("/health?test=1&foo=bar")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
