"""Tests for POST /repo/register and GET /repo/status endpoints."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from src.main import create_app

app = create_app()
client = TestClient(app)


def test_register_valid_path(tmp_path: Path) -> None:
    with patch("src.api.repository._run_indexing", new=AsyncMock()):
        response = client.post("/repo/register", json={"repo_path": str(tmp_path)})
    assert response.status_code == 200
    data = response.json()
    assert data["repo_path"] == str(tmp_path)
    assert data["status"] in ("queued", "indexing", "ready")


def test_register_invalid_path_returns_400() -> None:
    response = client.post("/repo/register", json={"repo_path": "/no/such/path/at/all"})
    assert response.status_code == 400


def test_status_unknown_repo_returns_404() -> None:
    response = client.get("/repo/status//no/such/repo")
    assert response.status_code == 404


def test_status_returns_current_state(tmp_path: Path) -> None:
    from src.api.repository import _jobs

    _jobs[str(tmp_path)] = "ready"
    response = client.get(f"/repo/status/{tmp_path}")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    del _jobs[str(tmp_path)]
