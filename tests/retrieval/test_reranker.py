"""Tests for src/retrieval/reranker.py."""

from typing import Any
from unittest.mock import MagicMock, patch

import numpy as np
from src.retrieval.qdrant_store import RetrievalResult
from src.retrieval.reranker import CrossEncoderReranker


def _make(content: str, score: float = 0.5) -> RetrievalResult:
    return RetrievalResult(
        content=content,
        score=score,
        path="test.py",
        symbol="func",
        start_line=1,
        end_line=10,
    )


def test_reranker_orders_by_score() -> None:
    mock_ce: Any = MagicMock()
    mock_ce.predict.return_value = np.array([0.3, 0.9, 0.1])

    with patch("src.retrieval.reranker.CrossEncoder", return_value=mock_ce):
        reranker = CrossEncoderReranker()

    candidates = [_make("low"), _make("high"), _make("lowest")]
    results = reranker.rerank("query", candidates, top_k=2)

    assert len(results) == 2
    assert results[0].content == "high"
    assert results[1].content == "low"


def test_reranker_respects_top_k() -> None:
    mock_ce: Any = MagicMock()
    mock_ce.predict.return_value = np.array([0.5, 0.8, 0.3, 0.9])

    with patch("src.retrieval.reranker.CrossEncoder", return_value=mock_ce):
        reranker = CrossEncoderReranker()

    candidates = [_make(f"doc{i}") for i in range(4)]
    results = reranker.rerank("query", candidates, top_k=2)
    assert len(results) == 2


def test_reranker_empty_candidates() -> None:
    mock_ce: Any = MagicMock()

    with patch("src.retrieval.reranker.CrossEncoder", return_value=mock_ce):
        reranker = CrossEncoderReranker()

    assert reranker.rerank("query", [], top_k=5) == []


def test_reranker_score_reflects_ce_output() -> None:
    mock_ce: Any = MagicMock()
    mock_ce.predict.return_value = np.array([0.75])

    with patch("src.retrieval.reranker.CrossEncoder", return_value=mock_ce):
        reranker = CrossEncoderReranker()

    results = reranker.rerank("query", [_make("only")], top_k=1)
    assert abs(results[0].score - 0.75) < 1e-6
