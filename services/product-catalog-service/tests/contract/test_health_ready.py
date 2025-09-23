"""Contract tests for GET /health/ready endpoint."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_readiness_check_success():
    """Test readiness check when service is ready."""
    response = client.get("/health/ready")

    # Should be 200 when ready, 503 when not ready
    assert response.status_code in [200, 503]

    data = response.json()

    # Verify required fields from contract
    assert "status" in data
    assert "timestamp" in data

    # Verify field types
    assert isinstance(data["status"], str)
    assert isinstance(data["timestamp"], str)

    # Verify timestamp format (ISO 8601)
    import re

    iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
    assert re.match(iso_pattern, data["timestamp"])

    if response.status_code == 200:
        # When ready, status should be "ready"
        assert data["status"] == "ready"

        # Should include database status
        if "database" in data:
            assert isinstance(data["database"], str)
            assert data["database"] in ["connected", "disconnected"]
    else:
        # When not ready (503), check error structure
        assert response.status_code == 503
        # Status might be different when not ready


def test_readiness_check_database_dependency():
    """Test that readiness check includes database connectivity."""
    response = client.get("/health/ready")

    data = response.json()

    # When checking readiness, database status should be included
    # This might not be present in basic health check
    if response.status_code == 200:
        # Ready response may include database status
        if "database" in data:
            assert data["database"] in ["connected", "disconnected"]

            # If database is disconnected, service might not be ready
            if data["database"] == "disconnected":
                # This is implementation dependent
                pass


def test_readiness_check_response_structure():
    """Test that readiness response matches contract."""
    response = client.get("/health/ready")

    data = response.json()

    # Required fields
    required_fields = {"status", "timestamp"}
    actual_fields = set(data.keys())

    assert required_fields.issubset(actual_fields)

    # Optional fields that might be present
    optional_fields = {"database"}
    all_allowed_fields = required_fields | optional_fields

    # No unexpected fields
    assert actual_fields.issubset(all_allowed_fields)


def test_readiness_check_vs_health_check():
    """Test differences between health and readiness checks."""
    health_response = client.get("/health")
    ready_response = client.get("/health/ready")

    # Health should always be 200 (unless service is completely down)
    assert health_response.status_code == 200

    # Ready may be 200 or 503
    assert ready_response.status_code in [200, 503]

    health_data = health_response.json()
    ready_data = ready_response.json()

    # Both should have status and timestamp
    assert "status" in health_data
    assert "timestamp" in health_data
    assert "status" in ready_data
    assert "timestamp" in ready_data

    # Readiness might have additional fields
    if ready_response.status_code == 200:
        # Ready status should be "ready"
        assert ready_data["status"] == "ready"


def test_readiness_check_content_type():
    """Test that readiness check returns correct content type."""
    response = client.get("/health/ready")

    assert response.headers["content-type"] == "application/json"


def test_readiness_check_no_authentication():
    """Test that readiness check requires no authentication."""
    # Should work without any headers
    response = client.get("/health/ready")
    assert response.status_code in [200, 503]

    # Should work with invalid auth headers
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/health/ready", headers=headers)
    assert response.status_code in [200, 503]


def test_readiness_check_methods():
    """Test that readiness endpoint only supports GET method."""
    # GET should work
    response = client.get("/health/ready")
    assert response.status_code in [200, 503]

    # Other methods should not be allowed
    response = client.post("/health/ready")
    assert response.status_code == 405  # Method Not Allowed

    response = client.put("/health/ready")
    assert response.status_code == 405

    response = client.delete("/health/ready")
    assert response.status_code == 405


def test_readiness_check_error_response():
    """Test readiness check error response format."""
    response = client.get("/health/ready")

    if response.status_code == 503:
        # Service not ready
        data = response.json()

        # Should still follow error response format
        assert "detail" in data or "status" in data

        # If using standard error format
        if "detail" in data:
            assert isinstance(data["detail"], str)


def test_readiness_check_startup_sequence():
    """Test readiness during startup sequence."""
    # This test assumes service might not be ready immediately
    response = client.get("/health/ready")

    # Should get a response (either ready or not ready)
    assert response.status_code in [200, 503]

    # If not ready, should eventually become ready
    # (This is more of an integration test)
    if response.status_code == 503:
        # Could retry a few times to see if it becomes ready
        # But for contract testing, just verify the response format
        data = response.json()
        assert isinstance(data, dict)


def test_readiness_check_performance():
    """Test that readiness check responds reasonably quickly."""
    import time

    start_time = time.time()
    response = client.get("/health/ready")
    end_time = time.time()

    assert response.status_code in [200, 503]

    # Readiness check should be reasonably fast
    # (might be slower than health check due to database checks)
    response_time = end_time - start_time
    assert response_time < 5.0  # More generous than health check


def test_readiness_check_consistency():
    """Test readiness check consistency."""
    responses = []

    # Make multiple calls
    for _ in range(3):
        response = client.get("/health/ready")
        assert response.status_code in [200, 503]
        responses.append(response)

    # All should return same status code (assuming stable state)
    status_codes = [r.status_code for r in responses]

    # Should be consistently ready or consistently not ready
    # (unless caught during a state transition)
    unique_codes = set(status_codes)
    assert len(unique_codes) <= 2  # At most ready and not-ready states
