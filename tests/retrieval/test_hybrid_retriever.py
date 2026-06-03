"""Tests for src/retrieval/hybrid_retriever.py."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from src.retrieval.hybrid_retriever import HybridRetriever, rrf_fusion
from src.retrieval.qdrant_store import RetrievalResult


def _make(path: str, start: int = 1, score: float = 0.5) -> RetrievalResult:
    return RetrievalResult(
        content=f"def func_{path}(): pass",
        score=score,
        path=path,
        symbol="func",
        start_line=start,
        end_line=start + 5,
    )


# ── RRF fusion ──────────────────────────────────────────────────────────────


def test_rrf_doc_in_both_lists_ranks_first() -> None:
    a = [_make("auth.py"), _make("user.py")]
    b = [_make("db.py"), _make("auth.py")]
    fused = rrf_fusion(a, b)
    assert fused[0].path == "auth.py"


def test_rrf_union_of_both_lists() -> None:
    a = [_make("a.py"), _make("b.py")]
    b = [_make("b.py"), _make("c.py")]
    paths = {r.path for r in rrf_fusion(a, b)}
    assert paths == {"a.py", "b.py", "c.py"}


def test_rrf_empty_inputs() -> None:
    assert rrf_fusion([], []) == []


def test_rrf_single_list() -> None:
    a = [_make("x.py"), _make("y.py")]
    fused = rrf_fusion(a, [])
    assert [r.path for r in fused] == ["x.py", "y.py"]


def test_rrf_score_is_positive() -> None:
    fused = rrf_fusion([_make("a.py")], [_make("b.py")])
    assert all(r.score > 0 for r in fused)


# ── HybridRetriever ──────────────────────────────────────────────────────────


@pytest.fixture
def corpus() -> list[RetrievalResult]:
    return [
        _make("auth.py", 1),
        _make("user.py", 1),
        _make("db.py", 1),
    ]


async def test_retrieve_returns_at_most_top_k(
    corpus: list[RetrievalResult],
) -> None:
    mock_qdrant: Any = AsyncMock()
    mock_qdrant.search.return_value = [
        MagicMock(
            score=0.9,
            payload={
                "content": "def login(): pass",
                "file_path": "auth.py",
                "symbol": "login",
                "start_line": 1,
                "end_line": 5,
            },
        )
    ]
    mock_openai: Any = AsyncMock()
    fake_emb: Any = MagicMock()
    fake_emb.embedding = [0.1] * 3072
    mock_openai.embeddings.create.return_value = MagicMock(data=[fake_emb])

    retriever = HybridRetriever(
        corpus=corpus,
        qdrant=mock_qdrant,
        openai_client=mock_openai,
        reranker=None,
    )
    results = await retriever.retrieve("login function", top_k=2)
    assert len(results) <= 2
    assert all(isinstance(r, RetrievalResult) for r in results)


async def test_retrieve_with_empty_corpus() -> None:
    mock_qdrant: Any = AsyncMock()
    mock_qdrant.search.return_value = []
    mock_openai: Any = AsyncMock()
    fake_emb: Any = MagicMock()
    fake_emb.embedding = [0.0] * 3072
    mock_openai.embeddings.create.return_value = MagicMock(data=[fake_emb])

    retriever = HybridRetriever(
        corpus=[],
        qdrant=mock_qdrant,
        openai_client=mock_openai,
        reranker=None,
    )
    results = await retriever.retrieve("anything", top_k=5)
    assert results == []


async def test_retrieve_calls_reranker_when_present(
    corpus: list[RetrievalResult],
) -> None:
    mock_qdrant: Any = AsyncMock()
    mock_qdrant.search.return_value = []
    mock_openai: Any = AsyncMock()
    fake_emb: Any = MagicMock()
    fake_emb.embedding = [0.0] * 3072
    mock_openai.embeddings.create.return_value = MagicMock(data=[fake_emb])

    mock_reranker: Any = MagicMock()
    mock_reranker.rerank.return_value = [corpus[0]]

    retriever = HybridRetriever(
        corpus=corpus,
        qdrant=mock_qdrant,
        openai_client=mock_openai,
        reranker=mock_reranker,
    )
    await retriever.retrieve("query", top_k=1)
    mock_reranker.rerank.assert_called_once()
