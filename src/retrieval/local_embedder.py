"""Local embedding using sentence-transformers (no external API required)."""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from src.config import get_settings


@lru_cache(maxsize=1)
def _get_local_model() -> SentenceTransformer:
    """Load and cache the local sentence-transformers model."""
    settings = get_settings()
    return SentenceTransformer(settings.local_embedding_model)


async def embed_local(texts: list[str]) -> list[list[float]]:
    """Embed texts using a local sentence-transformer model."""
    model = _get_local_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    return [emb.tolist() for emb in embeddings]


async def embed_local_query(query: str) -> list[float]:
    """Embed a single query string using local model."""
    model = _get_local_model()
    emb = model.encode(query, normalize_embeddings=True)
    return emb.tolist()
