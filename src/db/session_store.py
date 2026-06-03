"""In-memory session store for chat history."""

import time
import uuid
from collections import deque
from typing import Any

_MAX_SESSIONS = 1000
_TTL_SECONDS = 3600

# session_id → {created_at, messages: deque}
_store: dict[str, dict[str, Any]] = {}


def create_session() -> str:
    """Create a new session and return its ID."""
    _evict()
    session_id = str(uuid.uuid4())
    _store[session_id] = {"created_at": time.time(), "messages": deque(maxlen=50)}
    return session_id


def get_session(session_id: str) -> dict[str, Any] | None:
    """Return session data or None if not found / expired."""
    entry = _store.get(session_id)
    if entry is None:
        return None
    if time.time() - entry["created_at"] > _TTL_SECONDS:
        del _store[session_id]
        return None
    return entry


def append_message(session_id: str, role: str, content: str) -> None:
    """Append a message to the session history, creating if absent."""
    if session_id not in _store:
        _store[session_id] = {"created_at": time.time(), "messages": deque(maxlen=50)}
    _store[session_id]["messages"].append({"role": role, "content": content})


def _evict() -> None:
    """Remove expired sessions; if still full, drop oldest."""
    now = time.time()
    expired = [k for k, v in _store.items() if now - v["created_at"] > _TTL_SECONDS]
    for k in expired:
        del _store[k]
    while len(_store) >= _MAX_SESSIONS:
        oldest = min(_store, key=lambda k: _store[k]["created_at"])
        del _store[oldest]
