"""Tests for src/retrieval/qdrant_store.py."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

from src.retrieval.qdrant_store import RetrievalResult, embed_query, vector_search


async def test_embed_query_returns_floats() -> None:
    mock_openai: Any = AsyncMock()
    fake_emb: Any = MagicMock()
    fake_emb.embedding = [0.1] * 3072
    mock_openai.embeddings.create.return_value = MagicMock(data=[fake_emb])

    vec = await embed_query(mock_openai, "hello", "text-embedding-3-large")
    assert len(vec) == 3072
    assert all(isinstance(v, float) for v in vec)


async def test_vector_search_maps_payload_to_result() -> None:
    mock_qdrant: Any = AsyncMock()
    hit: Any = MagicMock()
    hit.score = 0.95
    hit.payload = {
        "content": "def login(): pass",
        "file_path": "auth.py",
        "symbol": "login",
        "start_line": 10,
        "end_line": 20,
    }
    mock_qdrant.query_points.return_value = MagicMock(points=[hit])

    results = await vector_search(mock_qdrant, [0.0] * 3072, top_k=5)
    assert len(results) == 1
    r = results[0]
    assert isinstance(r, RetrievalResult)
    assert r.path == "auth.py"
    assert r.symbol == "login"
    assert r.start_line == 10
    assert abs(r.score - 0.95) < 1e-6


async def test_vector_search_skips_missing_payload() -> None:
    mock_qdrant: Any = AsyncMock()
    hit: Any = MagicMock()
    hit.score = 0.5
    hit.payload = None
    mock_qdrant.query_points.return_value = MagicMock(points=[hit])

    results = await vector_search(mock_qdrant, [0.0] * 3072, top_k=5)
    assert results == []
