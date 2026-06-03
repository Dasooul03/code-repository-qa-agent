"""Hybrid retriever: dense + BM25 + RRF fusion + CrossEncoder rerank."""

from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient
from rank_bm25 import BM25Okapi

from src.config import get_settings
from src.retrieval.qdrant_store import (
    RetrievalResult,
    embed_query,
    load_corpus,
    vector_search,
)
from src.retrieval.reranker import CrossEncoderReranker

_RRF_K = 60
_DENSE_TOP_K = 20
_BM25_TOP_K = 20


def rrf_fusion(
    ranked_a: list[RetrievalResult],
    ranked_b: list[RetrievalResult],
    k: int = _RRF_K,
) -> list[RetrievalResult]:
    """Merge two ranked lists using Reciprocal Rank Fusion.

    RRF score = Σ 1 / (k + rank_i(d)) over all lists containing d.
    """
    rrf_scores: dict[str, float] = {}
    index: dict[str, RetrievalResult] = {}

    for rank, result in enumerate(ranked_a):
        doc_key = f"{result.path}:{result.start_line}"
        rrf_scores[doc_key] = rrf_scores.get(doc_key, 0.0) + 1.0 / (k + rank + 1)
        index[doc_key] = result

    for rank, result in enumerate(ranked_b):
        doc_key = f"{result.path}:{result.start_line}"
        rrf_scores[doc_key] = rrf_scores.get(doc_key, 0.0) + 1.0 / (k + rank + 1)
        if doc_key not in index:
            index[doc_key] = result

    return [
        RetrievalResult(
            content=index[doc_key].content,
            score=rrf_scores[doc_key],
            path=index[doc_key].path,
            symbol=index[doc_key].symbol,
            start_line=index[doc_key].start_line,
            end_line=index[doc_key].end_line,
        )
        for doc_key in sorted(rrf_scores, key=lambda x: rrf_scores[x], reverse=True)
    ]


class HybridRetriever:
    """Dense + BM25 hybrid retriever with RRF fusion and CrossEncoder rerank."""

    def __init__(
        self,
        corpus: list[RetrievalResult],
        qdrant: AsyncQdrantClient,
        openai_client: AsyncOpenAI,
        reranker: CrossEncoderReranker | None = None,
        dense_top_k: int = _DENSE_TOP_K,
        bm25_top_k: int = _BM25_TOP_K,
    ) -> None:
        self._corpus = corpus
        self._qdrant = qdrant
        self._openai = openai_client
        self._reranker = reranker
        self._dense_top_k = dense_top_k
        self._bm25_top_k = bm25_top_k
        self._bm25 = self._build_bm25(corpus)

    @staticmethod
    def _build_bm25(corpus: list[RetrievalResult]) -> BM25Okapi | None:
        if not corpus:
            return None
        tokenized = [doc.content.lower().split() for doc in corpus]
        return BM25Okapi(tokenized)

    def _bm25_search(self, query: str, top_k: int) -> list[RetrievalResult]:
        if not self._corpus or self._bm25 is None:
            return []
        tokens = query.lower().split()
        raw_scores = self._bm25.get_scores(tokens)
        ranked = sorted(
            zip(self._corpus, raw_scores, strict=True),
            key=lambda x: float(x[1]),
            reverse=True,
        )
        return [
            RetrievalResult(
                content=doc.content,
                score=float(score),
                path=doc.path,
                symbol=doc.symbol,
                start_line=doc.start_line,
                end_line=doc.end_line,
            )
            for doc, score in ranked[:top_k]
        ]

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """Run the full hybrid retrieval pipeline for a query."""
        settings = get_settings()
        query_vec = await embed_query(self._openai, query, settings.embedding_model)
        dense = await vector_search(self._qdrant, query_vec, self._dense_top_k)
        bm25 = self._bm25_search(query, self._bm25_top_k)
        fused = rrf_fusion(dense, bm25)

        if self._reranker is not None:
            return self._reranker.rerank(query, fused[: top_k * 4], top_k)
        return fused[:top_k]


async def build_retriever(
    qdrant_url: str | None = None,
    openai_api_key: str | None = None,
    enable_reranker: bool = True,
) -> HybridRetriever:
    """Build a HybridRetriever, loading the corpus from Qdrant."""
    settings = get_settings()
    qdrant = AsyncQdrantClient(url=qdrant_url or settings.qdrant_url)
    openai_client = AsyncOpenAI(api_key=openai_api_key or settings.openai_api_key)
    corpus = await load_corpus(qdrant)
    reranker = CrossEncoderReranker() if enable_reranker else None
    return HybridRetriever(
        corpus=corpus,
        qdrant=qdrant,
        openai_client=openai_client,
        reranker=reranker,
    )
