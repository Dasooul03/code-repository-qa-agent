"""Tests for GET /session/{id} endpoint."""

from fastapi.testclient import TestClient
from src.db import session_store
from src.main import create_app

app = create_app()
client = TestClient(app)


def test_get_session_not_found() -> None:
    response = client.get("/session/does-not-exist")
    assert response.status_code == 404


def test_get_session_returns_messages() -> None:
    sid = session_store.create_session()
    session_store.append_message(sid, "user", "hello")
    session_store.append_message(sid, "assistant", "hi there")

    response = client.get(f"/session/{sid}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == sid
    assert len(data["messages"]) == 2
    assert data["messages"][0]["role"] == "user"
    assert data["messages"][1]["content"] == "hi there"


def test_get_session_empty_history() -> None:
    sid = session_store.create_session()
    response = client.get(f"/session/{sid}")
    assert response.status_code == 200
    assert response.json()["messages"] == []
