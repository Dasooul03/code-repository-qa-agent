# Phase 2: Hybrid Retrieval

**Commit:** `69db767 feat(phase-2): implement hybrid retrieval`
**Date:** 2026-06-03
**Agent:** Claude (claude-sonnet-4-6)
**Status:** COMPLETE

## Goal

Implement hybrid retrieval: Dense (Qdrant vector search) + BM25 keyword search, fused with RRF, optionally reranked with CrossEncoder.

## Files Created

| File | Purpose |
|------|---------|
| `src/retrieval/qdrant_store.py` | Dense vector search via `AsyncQdrantClient.query_points()` |
| `src/retrieval/hybrid_retriever.py` | Full hybrid pipeline: embed → dense → BM25 → RRF → rerank |
| `src/retrieval/reranker.py` | CrossEncoder reranker (sentence-transformers) |
| `tests/retrieval/test_qdrant_store.py` | Qdrant search tests with mocked client |
| `tests/retrieval/test_hybrid_retriever.py` | RRF fusion and retrieval pipeline tests |
| `tests/retrieval/test_reranker.py` | CrossEncoder reranker tests |

## Key Implementation Details

### qdrant_store.py — qdrant-client 1.18 API
```python
# qdrant-client 1.18 removed search() in favour of query_points()
async def vector_search(qdrant, query_vector, top_k) -> list[RetrievalResult]:
    response = await qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )
    return [RetrievalResult(...) for h in response.points if h.payload]
```

### hybrid_retriever.py — RRF fusion
```python
def rrf_fusion(ranked_a, ranked_b, k=60) -> list[RetrievalResult]:
    for rank, doc in enumerate(ranked_a):
        rrf_scores[key(doc)] += 1.0 / (k + rank + 1)
    for rank, doc in enumerate(ranked_b):
        rrf_scores[key(doc)] += 1.0 / (k + rank + 1)
    # sort descending, rebuild RetrievalResult with fused score
```
Documents appearing in both lists accumulate higher scores.

### hybrid_retriever.py — empty corpus guard
```python
def _build_bm25(corpus: list[RetrievalResult]) -> BM25Okapi | None:
    if not corpus:
        return None   # BM25Okapi([[]]) crashes in _calc_idf
    return BM25Okapi([doc.content.lower().split() for doc in corpus])
```
`BM25Okapi([[]])` raises `ZeroDivisionError` when the only document has no words.

### reranker.py — CrossEncoder
```python
class CrossEncoderReranker:
    def rerank(self, query, candidates, top_k) -> list[RetrievalResult]:
        pairs = [(query, c.content) for c in candidates]
        raw_scores = self._model.predict(pairs)  # type: ignore[arg-type]
        # sentence-transformers 5.x predict() has complex union input type
```

## Bugs Fixed During Validation

| Error | Fix |
|-------|-----|
| `AsyncQdrantClient.search` not found | Rewrote to use `query_points()` (qdrant-client 1.18 API change) |
| `BM25Okapi` ZeroDivisionError on empty corpus | Return `None` from `_build_bm25` when corpus is empty |
| `CrossEncoder.predict` arg-type | Added `# type: ignore[arg-type]` (sentence-transformers 5.x union type) |
| Test mock `.search` → `.query_points` | Updated all test mocks to match new API |

## Commands Run

```
uv sync --all-groups
uv run black src tests    → reformatted files
uv run ruff check --fix   → auto-fixed imports
uv run mypy src tests     → success
uv run pytest             → 37/37 passed
git commit 69db767
```

## Validation

- black: ✓ | ruff: ✓ | mypy: ✓ | pytest: 37/37 ✓

## Architecture Note

Retrieval pipeline:
```
Query
  → embed (text-embedding-3-large, 3072-dim)
  → Qdrant dense search (top_k×4 candidates)
  → BM25 keyword search (in-memory, same corpus)
  → RRF fusion (k=60)
  → CrossEncoder rerank (optional, cross-encoder/ms-marco-MiniLM-L-6-v2)
  → top_k results
```

## Next Phase

Phase 3 — LangGraph Agent
