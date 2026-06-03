"""Tests for the health endpoint."""

from fastapi.testclient import TestClient
from src.main import app


def test_health_returns_ok() -> None:
    """The health endpoint returns the expected status payload."""

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
