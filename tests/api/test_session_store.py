"""Tests for in-memory session store."""

import time

from src.db.session_store import (
    _TTL_SECONDS,
    _store,
    append_message,
    create_session,
    get_session,
)


def test_create_session_returns_unique_ids() -> None:
    s1 = create_session()
    s2 = create_session()
    assert s1 != s2


def test_get_session_returns_entry() -> None:
    sid = create_session()
    entry = get_session(sid)
    assert entry is not None
    assert "messages" in entry


def test_get_session_unknown_returns_none() -> None:
    assert get_session("no-such-id") is None


def test_append_message_stores_messages() -> None:
    sid = create_session()
    append_message(sid, "user", "hello")
    append_message(sid, "assistant", "hi")
    entry = get_session(sid)
    assert entry is not None
    msgs = list(entry["messages"])
    assert msgs[0] == {"role": "user", "content": "hello"}
    assert msgs[1] == {"role": "assistant", "content": "hi"}


def test_get_session_expired_returns_none() -> None:
    sid = create_session()
    _store[sid]["created_at"] = time.time() - _TTL_SECONDS - 1
    assert get_session(sid) is None
    assert sid not in _store
