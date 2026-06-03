"""Tests for POST /chat SSE endpoint."""

import json
from typing import Any
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from src.main import create_app

app = create_app()
client = TestClient(app, raise_server_exceptions=False)


def _collect_sse(response: Any) -> list[dict[str, Any]]:
    """Parse raw SSE response text into a list of JSON objects."""
    events = []
    for line in response.text.splitlines():
        line = line.strip()
        if line.startswith("data: "):
            events.append(json.loads(line[6:]))
    return events


def test_chat_streams_answer() -> None:
    with (
        patch("src.api.chat.run_agent", new=AsyncMock(return_value="The answer is 42.")),
        patch("src.api.chat._make_llm", return_value=None),
    ):
        response = client.post(
            "/chat",
            json={"query": "what is the answer?", "repo_root": "."},
        )

    assert response.status_code == 200
    events = _collect_sse(response)
    assert any("delta" in e for e in events)
    done_events = [e for e in events if e.get("done")]
    assert len(done_events) == 1
    assert "session_id" in done_events[0]


def test_chat_creates_session_automatically() -> None:
    with (
        patch("src.api.chat.run_agent", new=AsyncMock(return_value="hello")),
        patch("src.api.chat._make_llm", return_value=None),
    ):
        response = client.post("/chat", json={"query": "hi", "repo_root": "."})

    events = _collect_sse(response)
    done = next(e for e in events if e.get("done"))
    assert done["session_id"]


def test_chat_invalid_session_returns_404() -> None:
    response = client.post(
        "/chat",
        json={"query": "hi", "session_id": "nonexistent-id", "repo_root": "."},
    )
    assert response.status_code == 404


def test_chat_empty_query_rejected() -> None:
    response = client.post("/chat", json={"query": "", "repo_root": "."})
    assert response.status_code == 422
