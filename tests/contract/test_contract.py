"""Contract tests for the YouTube parser.

These tests verify that the parser conforms to the unified parser contract.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.bootstrap import create_app


@pytest.fixture
def client() -> TestClient:
    """Create a test client.

    Returns:
        TestClient instance
    """
    app = create_app()
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncClient:
    """Create an async test client.

    Yields:
        AsyncClient instance
    """
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


class TestHealthEndpoint:
    """Tests for GET /api/v1/health."""

    def test_health_returns_up(self, client: TestClient) -> None:
        """Test that health endpoint returns UP status."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "UP"


class TestCapabilitiesEndpoint:
    """Tests for GET /api/v1/capabilities."""

    def test_capabilities_returns_platform(self, client: TestClient) -> None:
        """Test that capabilities returns youtube platform."""
        response = client.get("/api/v1/capabilities")

        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "youtube"

    def test_capabilities_returns_supported_source_types(self, client: TestClient) -> None:
        """Test that capabilities returns supported source types."""
        response = client.get("/api/v1/capabilities")

        assert response.status_code == 200
        data = response.json()
        assert "video" in data["supportedSourceTypes"]
        assert "share_text" in data["supportedSourceTypes"]

    def test_capabilities_returns_features(self, client: TestClient) -> None:
        """Test that capabilities returns features object."""
        response = client.get("/api/v1/capabilities")

        assert response.status_code == 200
        data = response.json()
        assert "features" in data
        assert isinstance(data["features"], dict)


class TestParseEndpoint:
    """Tests for POST /api/v1/parse."""

    # Real YouTube video IDs for testing
    RICKROLL_ID = "dQw4w9WgXcQ"

    def test_parse_watch_url(self, client: TestClient) -> None:
        """Test parsing a watch URL."""
        response = client.post(
            "/api/v1/parse",
            json={
                "input": {
                    "sourceUrl": f"https://www.youtube.com/watch?v={self.RICKROLL_ID}",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["platform"] == "youtube"
        assert data["data"]["externalId"] == self.RICKROLL_ID
        assert data["data"]["canonicalUrl"] == f"https://www.youtube.com/watch?v={self.RICKROLL_ID}"
        # Should have real title now
        assert data["data"]["title"] is not None

    def test_parse_short_url(self, client: TestClient) -> None:
        """Test parsing a youtu.be short URL."""
        response = client.post(
            "/api/v1/parse",
            json={
                "input": {
                    "sourceUrl": f"https://youtu.be/{self.RICKROLL_ID}",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["externalId"] == self.RICKROLL_ID
        assert data["data"]["canonicalUrl"] == f"https://www.youtube.com/watch?v={self.RICKROLL_ID}"

    def test_parse_shorts_url(self, client: TestClient) -> None:
        """Test parsing a shorts URL."""
        # Using a real shorts video ID
        response = client.post(
            "/api/v1/parse",
            json={
                "input": {
                    "sourceUrl": f"https://www.youtube.com/shorts/{self.RICKROLL_ID}",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["externalId"] == self.RICKROLL_ID
        assert data["data"]["canonicalUrl"] == f"https://www.youtube.com/watch?v={self.RICKROLL_ID}"

    def test_parse_live_url(self, client: TestClient) -> None:
        """Test parsing a live URL."""
        # Using the same video ID for live URL format test
        response = client.post(
            "/api/v1/parse",
            json={
                "input": {
                    "sourceUrl": f"https://www.youtube.com/live/{self.RICKROLL_ID}",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["externalId"] == self.RICKROLL_ID

    def test_parse_share_text(self, client: TestClient) -> None:
        """Test parsing share text containing a URL."""
        response = client.post(
            "/api/v1/parse",
            json={
                "input": {
                    "sourceText": f"看看这个视频 https://youtu.be/{self.RICKROLL_ID} 很有意思",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["externalId"] == self.RICKROLL_ID

    def test_parse_returns_request_id(self, client: TestClient) -> None:
        """Test that response includes request ID."""
        response = client.post(
            "/api/v1/parse",
            json={
                "requestId": "test-request-123",
                "input": {
                    "sourceUrl": f"https://www.youtube.com/watch?v={self.RICKROLL_ID}",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["requestId"] == "test-request-123"

    def test_parse_generates_request_id(self, client: TestClient) -> None:
        """Test that request ID is generated if not provided."""
        response = client.post(
            "/api/v1/parse",
            json={
                "input": {
                    "sourceUrl": f"https://www.youtube.com/watch?v={self.RICKROLL_ID}",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["requestId"].startswith("req_")

    def test_parse_returns_parser_version(self, client: TestClient) -> None:
        """Test that response includes parser version."""
        response = client.post(
            "/api/v1/parse",
            json={
                "input": {
                    "sourceUrl": f"https://www.youtube.com/watch?v={self.RICKROLL_ID}",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "parserVersion" in data["meta"]

    def test_parse_returns_real_metadata(self, client: TestClient) -> None:
        """Test that real metadata is returned."""
        response = client.post(
            "/api/v1/parse",
            json={
                "input": {
                    "sourceUrl": f"https://www.youtube.com/watch?v={self.RICKROLL_ID}",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Check real metadata is present
        payload = data["data"]
        assert payload["title"] is not None
        assert "Never Gonna Give You Up" in payload["title"] or "Rick Astley" in payload["title"]
        assert payload["author"] is not None
        assert payload["author"]["name"] is not None


class TestParseErrors:
    """Tests for error cases in POST /api/v1/parse."""

    def test_invalid_input_no_url(self, client: TestClient) -> None:
        """Test error when no URL is provided."""
        response = client.post(
            "/api/v1/parse",
            json={
                "input": {
                    "sourceText": "这是一个没有链接的文本",
                },
            },
        )

        # HTTP 400 for invalid input
        assert response.status_code == 400
        data = response.json()
        # FastAPI HTTPException wraps response in "detail"
        envelope = data.get("detail", data)
        assert envelope["success"] is False
        assert envelope["error"]["code"] == "INVALID_INPUT"
        assert envelope["data"] is None

    def test_unsupported_url(self, client: TestClient) -> None:
        """Test error when URL is not a YouTube URL."""
        response = client.post(
            "/api/v1/parse",
            json={
                "input": {
                    "sourceUrl": "https://vimeo.com/123456",
                },
            },
        )

        # HTTP 400 for unsupported URL
        assert response.status_code == 400
        data = response.json()
        # FastAPI HTTPException wraps response in "detail"
        envelope = data.get("detail", data)
        assert envelope["success"] is False
        assert envelope["error"]["code"] == "UNSUPPORTED_URL"

    def test_missing_input(self, client: TestClient) -> None:
        """Test error when input is missing."""
        response = client.post("/api/v1/parse", json={})

        assert response.status_code == 422  # Validation error


class TestEnvelope:
    """Tests for the API envelope structure."""

    RICKROLL_ID = "dQw4w9WgXcQ"

    def test_success_envelope_structure(self, client: TestClient) -> None:
        """Test that success response has correct envelope structure."""
        response = client.post(
            "/api/v1/parse",
            json={
                "input": {
                    "sourceUrl": f"https://www.youtube.com/watch?v={self.RICKROLL_ID}",
                },
            },
        )

        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "error" in data
        assert "meta" in data

        # On success, error should be null
        assert data["success"] is True
        assert data["error"] is None
        assert data["data"] is not None

    def test_error_envelope_structure(self, client: TestClient) -> None:
        """Test that error response has correct envelope structure."""
        response = client.post(
            "/api/v1/parse",
            json={
                "input": {
                    "sourceUrl": "https://vimeo.com/123",
                },
            },
        )

        data = response.json()
        # FastAPI HTTPException wraps response in "detail"
        envelope = data.get("detail", data)

        assert "success" in envelope
        assert "data" in envelope
        assert "error" in envelope
        assert "meta" in envelope

        # On error, data should be null
        assert envelope["success"] is False
        assert envelope["data"] is None
        assert envelope["error"] is not None
        assert "code" in envelope["error"]
        assert "message" in envelope["error"]
        assert "retryable" in envelope["error"]