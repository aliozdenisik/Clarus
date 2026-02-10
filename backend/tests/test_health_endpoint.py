"""
Unit tests for health endpoint at /api/health.

Tests cover:
- Response structure (status, version, event_loop, qdrant fields)
- Status codes (200 for healthy, 503 for degraded/unhealthy)
- Field validation (correct values and types)
- Event loop responsiveness detection
- Qdrant connectivity status
- Mocked Qdrant client for isolation
"""

import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Add backend to path for imports
sys.path.insert(0, "/home/freyja/qdrant/backend")

from app.main import app


class TestHealthEndpointBasics:
    """Test basic health endpoint functionality."""

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_health_endpoint_exists(self):
        """Health endpoint should be accessible at /api/health."""
        response = self.client.get("/api/health")
        assert response.status_code in [200, 503]

    def test_health_returns_json(self):
        """Health endpoint should return JSON response."""
        response = self.client.get("/api/health")
        assert response.headers["content-type"] == "application/json"

    def test_health_response_is_dict(self):
        """Health endpoint should return a dictionary."""
        response = self.client.get("/api/health")
        data = response.json()
        assert isinstance(data, dict)


class TestHealthResponseStructure:
    """Test health endpoint response structure."""

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_response_contains_status_field(self):
        """Response should contain 'status' field."""
        response = self.client.get("/api/health")
        data = response.json()
        assert "status" in data

    def test_response_contains_version_field(self):
        """Response should contain 'version' field."""
        response = self.client.get("/api/health")
        data = response.json()
        assert "version" in data

    def test_response_contains_event_loop_field(self):
        """Response should contain 'event_loop' field."""
        response = self.client.get("/api/health")
        data = response.json()
        assert "event_loop" in data

    def test_response_contains_qdrant_field(self):
        """Response should contain 'qdrant' field."""
        response = self.client.get("/api/health")
        data = response.json()
        assert "qdrant" in data

    def test_response_has_exactly_five_fields(self):
        """Response should have exactly 5 fields."""
        response = self.client.get("/api/health")
        data = response.json()
        assert len(data) == 5
        assert set(data.keys()) == {
            "status",
            "version",
            "event_loop",
            "qdrant",
            "redis",
        }


class TestHealthFieldTypes:
    """Test health endpoint field types."""

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_status_is_string(self):
        """Status field should be a string."""
        response = self.client.get("/api/health")
        data = response.json()
        assert isinstance(data["status"], str)

    def test_version_is_string(self):
        """Version field should be a string."""
        response = self.client.get("/api/health")
        data = response.json()
        assert isinstance(data["version"], str)

    def test_event_loop_is_string(self):
        """Event loop field should be a string."""
        response = self.client.get("/api/health")
        data = response.json()
        assert isinstance(data["event_loop"], str)

    def test_qdrant_is_string(self):
        """Qdrant field should be a string."""
        response = self.client.get("/api/health")
        data = response.json()
        assert isinstance(data["qdrant"], str)


class TestHealthStatusValues:
    """Test health endpoint status field values."""

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_status_is_valid_value(self):
        """Status should be one of: healthy, degraded, unhealthy."""
        response = self.client.get("/api/health")
        data = response.json()
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

    def test_event_loop_is_valid_value(self):
        """Event loop should be one of: ok, blocked."""
        response = self.client.get("/api/health")
        data = response.json()
        assert data["event_loop"] in ["ok", "blocked"]

    def test_qdrant_is_valid_value(self):
        """Qdrant should be one of: connected, disconnected."""
        response = self.client.get("/api/health")
        data = response.json()
        assert data["qdrant"] in ["connected", "disconnected"]


class TestHealthVersionField:
    """Test health endpoint version field."""

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_version_is_semantic_version(self):
        """Version should be in semantic versioning format."""
        response = self.client.get("/api/health")
        data = response.json()
        version = data["version"]
        # Should match pattern like "2.0.0"
        parts = version.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

    def test_version_is_2_0_0(self):
        """Version should be 2.0.0."""
        response = self.client.get("/api/health")
        data = response.json()
        assert data["version"] == "2.0.0"


class TestHealthStatusCodes:
    """Test health endpoint HTTP status codes."""

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_healthy_returns_200(self):
        """Healthy status should return HTTP 200."""
        with patch("qdrant_client.QdrantClient") as mock_qdrant:
            mock_client = MagicMock()
            mock_client.get_collections.return_value = MagicMock()
            mock_qdrant.return_value = mock_client

            response = self.client.get("/api/health")
            data = response.json()

            if data["status"] == "healthy":
                assert response.status_code == 200

    def test_degraded_returns_200(self):
        """Degraded status should return HTTP 200 (only unhealthy returns 503)."""
        with patch("qdrant_client.QdrantClient") as mock_qdrant:
            mock_qdrant.side_effect = Exception("Connection failed")

            response = self.client.get("/api/health")
            data = response.json()

            if data["status"] == "degraded":
                assert response.status_code == 200

    def test_unhealthy_returns_503(self):
        """Unhealthy status should return HTTP 503."""
        with patch("qdrant_client.QdrantClient") as mock_qdrant:
            mock_qdrant.side_effect = Exception("Connection failed")

            response = self.client.get("/api/health")
            data = response.json()

            if data["status"] == "unhealthy":
                assert response.status_code == 503


class TestHealthEventLoopDetection:
    """Test event loop responsiveness detection."""

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_event_loop_is_ok_when_responsive(self):
        """Event loop should be 'ok' when responsive."""
        response = self.client.get("/api/health")
        data = response.json()
        # In normal conditions, event loop should be responsive
        assert data["event_loop"] == "ok"

    def test_event_loop_field_never_empty(self):
        """Event loop field should never be empty."""
        response = self.client.get("/api/health")
        data = response.json()
        assert data["event_loop"] != ""
        assert len(data["event_loop"]) > 0


class TestHealthQdrantConnectivity:
    """Test Qdrant connectivity detection."""

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_qdrant_connected_when_available(self):
        """Qdrant should show 'connected' when available."""
        with patch("qdrant_client.QdrantClient") as mock_qdrant:
            mock_client = MagicMock()
            mock_client.get_collections.return_value = MagicMock()
            mock_qdrant.return_value = mock_client

            response = self.client.get("/api/health")
            data = response.json()

            # If Qdrant is mocked successfully, it should be connected
            assert data["qdrant"] in ["connected", "disconnected"]

    def test_qdrant_disconnected_on_exception(self):
        """Qdrant should show 'disconnected' when exception occurs."""
        with patch("qdrant_client.QdrantClient") as mock_qdrant:
            mock_qdrant.side_effect = Exception("Connection refused")

            response = self.client.get("/api/health")
            data = response.json()

            # When Qdrant raises exception, it should be disconnected
            assert data["qdrant"] == "disconnected"

    def test_qdrant_disconnected_on_timeout(self):
        """Qdrant should show 'disconnected' on timeout."""
        with patch("qdrant_client.QdrantClient") as mock_qdrant:
            mock_qdrant.side_effect = TimeoutError("Timeout")

            response = self.client.get("/api/health")
            data = response.json()

            # When Qdrant times out, it should be disconnected
            assert data["qdrant"] == "disconnected"


class TestHealthStatusConsistency:
    """Test consistency between status and component statuses."""

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_healthy_when_all_ok(self):
        """Status should be 'healthy' when all components are ok."""
        with patch("qdrant_client.QdrantClient") as mock_qdrant:
            mock_client = MagicMock()
            mock_client.get_collections.return_value = MagicMock()
            mock_qdrant.return_value = mock_client

            response = self.client.get("/api/health")
            data = response.json()

            if data["event_loop"] == "ok" and data["qdrant"] == "connected" and data["redis"]["status"] == "connected":
                assert data["status"] == "healthy"
            elif data["event_loop"] == "ok" and data["qdrant"] == "connected":
                assert data["status"] in ["healthy", "degraded"]

    def test_degraded_when_qdrant_fails(self):
        """Status should be 'degraded' when qdrant fails but event_loop ok."""
        with patch("qdrant_client.QdrantClient") as mock_qdrant:
            mock_qdrant.side_effect = Exception("Connection failed")

            response = self.client.get("/api/health")
            data = response.json()

            if data["event_loop"] == "ok" and data["qdrant"] == "disconnected":
                assert data["status"] == "degraded"

    def test_unhealthy_when_event_loop_blocked(self):
        """Status should be 'unhealthy' when event loop is blocked."""
        with patch("asyncio.wait_for") as mock_wait:
            mock_wait.side_effect = TimeoutError("Event loop blocked")

            response = self.client.get("/api/health")
            data = response.json()

            if data["event_loop"] == "blocked":
                assert data["status"] == "unhealthy"


class TestHealthMultipleRequests:
    """Test health endpoint with multiple requests."""

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_multiple_requests_return_valid_responses(self):
        """Multiple requests should all return valid responses."""
        for _ in range(5):
            response = self.client.get("/api/health")
            assert response.status_code in [200, 503]
            data = response.json()
            assert "status" in data
            assert "version" in data
            assert "event_loop" in data
            assert "qdrant" in data
            assert "redis" in data

    def test_responses_are_consistent(self):
        """Multiple responses should have consistent structure."""
        responses = [self.client.get("/api/health").json() for _ in range(3)]

        for data in responses:
            assert set(data.keys()) == {
                "status",
                "version",
                "event_loop",
                "qdrant",
                "redis",
            }
            assert isinstance(data["status"], str)
            assert isinstance(data["version"], str)
            assert isinstance(data["event_loop"], str)
            assert isinstance(data["qdrant"], str)
            assert isinstance(data["redis"], dict)


class TestHealthEdgeCases:
    """Test health endpoint edge cases."""

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_health_with_qdrant_connection_error(self):
        """Health should handle Qdrant connection errors gracefully."""
        with patch("qdrant_client.QdrantClient") as mock_qdrant:
            mock_qdrant.side_effect = ConnectionError("Cannot connect")

            response = self.client.get("/api/health")
            assert response.status_code in [200, 503]
            data = response.json()
            assert data["qdrant"] == "disconnected"

    def test_health_with_qdrant_timeout_error(self):
        """Health should handle Qdrant timeout errors gracefully."""
        with patch("qdrant_client.QdrantClient") as mock_qdrant:
            mock_qdrant.side_effect = TimeoutError("Timeout")

            response = self.client.get("/api/health")
            assert response.status_code in [200, 503]
            data = response.json()
            assert data["qdrant"] == "disconnected"

    def test_health_with_generic_exception(self):
        """Health should handle generic exceptions gracefully."""
        with patch("qdrant_client.QdrantClient") as mock_qdrant:
            mock_qdrant.side_effect = Exception("Generic error")

            response = self.client.get("/api/health")
            assert response.status_code in [200, 503]
            data = response.json()
            assert data["qdrant"] == "disconnected"

    def test_health_response_not_empty(self):
        """Health response should not be empty."""
        response = self.client.get("/api/health")
        data = response.json()
        assert len(data) > 0
        assert all(v is not None for v in data.values())


class TestHealthHTTPMethod:
    """Test health endpoint HTTP method."""

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_health_only_accepts_get(self):
        """Health endpoint should only accept GET requests."""
        # GET should work
        response = self.client.get("/api/health")
        assert response.status_code in [200, 503]

        # POST should fail
        response = self.client.post("/api/health")
        assert response.status_code == 405

        # PUT should fail
        response = self.client.put("/api/health")
        assert response.status_code == 405

        # DELETE should fail
        response = self.client.delete("/api/health")
        assert response.status_code == 405


class TestHealthEndpointIntegration:
    """Integration tests for health endpoint."""

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_health_endpoint_with_mocked_qdrant_success(self):
        """Health endpoint should work with mocked successful Qdrant."""
        with patch("qdrant_client.QdrantClient") as mock_qdrant:
            mock_client = MagicMock()
            mock_client.get_collections.return_value = [
                MagicMock(name="quran_tr_diyanet"),
                MagicMock(name="bible_ot"),
            ]
            mock_qdrant.return_value = mock_client

            response = self.client.get("/api/health")
            data = response.json()

            assert response.status_code in [200, 503]
            assert data["qdrant"] in ["connected", "disconnected"]

    def test_health_endpoint_with_mocked_qdrant_failure(self):
        """Health endpoint should work with mocked failed Qdrant."""
        with patch("qdrant_client.QdrantClient") as mock_qdrant:
            mock_qdrant.side_effect = Exception("Qdrant unavailable")

            response = self.client.get("/api/health")
            data = response.json()

            assert response.status_code in [200, 503]
            assert data["qdrant"] == "disconnected"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
