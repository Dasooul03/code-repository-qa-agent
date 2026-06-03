"""CrossEncoder reranker using sentence-transformers."""

from sentence_transformers import CrossEncoder

from src.retrieval.qdrant_store import RetrievalResult

DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class CrossEncoderReranker:
    """Reranks retrieval candidates using a cross-encoder model."""

    def __init__(self, model_name: str = DEFAULT_MODEL) -> None:
        self._model: CrossEncoder = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        candidates: list[RetrievalResult],
        top_k: int,
    ) -> list[RetrievalResult]:
        """Return top_k candidates sorted by cross-encoder score."""
        if not candidates:
            return []
        pairs = [(query, c.content) for c in candidates]
        raw_scores = self._model.predict(pairs)  # type: ignore[arg-type]
        scored = sorted(
            zip(candidates, raw_scores, strict=True),
            key=lambda x: float(x[1]),
            reverse=True,
        )
        return [
            RetrievalResult(
                content=c.content,
                score=float(s),
                path=c.path,
                symbol=c.symbol,
                start_line=c.start_line,
                end_line=c.end_line,
            )
            for c, s in scored[:top_k]
        ]
