# Phase 5: FastAPI API

**Commit:** `5dac581 feat(phase-5): implement fastapi api`
**Date:** 2026-06-03
**Agent:** Claude (claude-sonnet-4-6)
**Status:** COMPLETE

## Goal

Implement all FastAPI endpoints: SSE-streaming chat, repo registration, session history.

## Files Created / Modified

| File | Purpose |
|------|---------|
| `src/api/chat.py` | `POST /chat` — SSE streaming agent execution |
| `src/api/repository.py` | `POST /repo/register`, `GET /repo/status/{path}` |
| `src/api/session.py` | `GET /session/{id}` — session history lookup |
| `src/db/session_store.py` | In-memory session store with TTL eviction |
| `src/main.py` | Updated to wire all three new routers |
| `tests/api/test_chat.py` | 4 tests for chat SSE endpoint |
| `tests/api/test_repository.py` | 4 tests for repo endpoints |
| `tests/api/test_session.py` | 3 tests for session endpoint |
| `tests/api/test_session_store.py` | 5 tests for session store internals |

## API Contract

### POST /chat
```json
// Request
{"query": "...", "session_id": "optional-uuid", "repo_root": "."}

// SSE stream
data: {"delta": "chunk of answer text"}
data: {"delta": "more text"}
data: {"done": true, "session_id": "uuid"}
```

### POST /repo/register
```json
// Request
{"repo_path": "/absolute/path/to/repo"}

// Response
{"repo_path": "/absolute/path/to/repo", "status": "queued"}
```

### GET /repo/status/{repo_path}
```json
{"repo_path": "...", "status": "indexing|ready|error: ..."}
```

### GET /session/{id}
```json
{"session_id": "uuid", "messages": [{"role": "user", "content": "..."}]}
```

## Key Implementation Details

### SSE streaming in `_token_stream`
```python
async def _token_stream(query, repo_root, session_id, settings):
    llm = _make_llm(settings)
    try:
        answer = await run_agent(query, llm, repo_root=repo_root)
    except Exception as exc:
        yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        return

    # Emit in 80-char chunks with await asyncio.sleep(0) for event loop yield
    for i in range(0, len(answer), 80):
        yield f"data: {json.dumps({'delta': answer[i:i+80]})}\n\n"
        await asyncio.sleep(0)

    yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"
```

### Session store eviction
```python
_MAX_SESSIONS = 1000
_TTL_SECONDS = 3600

def _evict():
    # Remove expired sessions first; if still full, drop oldest
```

### Background indexing
```python
@router.post("/register")
async def register_repository(body, background_tasks, settings):
    background_tasks.add_task(_run_indexing, repo_path, settings)
    _jobs[repo_path] = "queued"
```

## Bugs Fixed During Validation

| Error | Fix |
|-------|-----|
| `_make_llm` raises with no API key in tests | Mocked `src.api.chat._make_llm` alongside `run_agent` in SSE tests |
| Unused imports in repository.py (asyncio, duplicate index_repository) | Removed via ruff --fix |
| Missing type annotation on `_collect_sse` helper | Added `Any` and `dict[str, Any]` |

## Commands Run

```
uv run black src/api src/db tests/api  → 1 file reformatted
uv run ruff check --fix                → 7 auto-fixed
uv run mypy src/api src/db tests/api   → success (12 files)
uv run pytest tests/api -v             → 16/16 passed
uv run pytest                          → 104/104 passed
git commit 5dac581
```

## Validation

- black: ✓ | ruff: ✓ | mypy: ✓ | pytest: 104/104 ✓

## Next Phase

Phase 6 — React Web UI (chat window, code citations, repo management, session history)
