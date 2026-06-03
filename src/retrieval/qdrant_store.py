"""Qdrant vector store operations for retrieval."""

from dataclasses import dataclass
from typing import Any

from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient

# Must match the collection name used in src/ingestion/indexer.py
COLLECTION_NAME = "code_chunks"


@dataclass
class RetrievalResult:
    """A retrieved code chunk."""

    content: str
    score: float
    path: str
    symbol: str
    start_line: int
    end_line: int


async def embed_query(client: AsyncOpenAI, query: str, model: str) -> list[float]:
    """Embed a single query string."""
    response = await client.embeddings.create(input=[query], model=model)
    return response.data[0].embedding


async def vector_search(
    qdrant: AsyncQdrantClient,
    query_vector: list[float],
    top_k: int,
) -> list[RetrievalResult]:
    """Search Qdrant by vector similarity and return ranked results."""
    response = await qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )
    return [
        RetrievalResult(
            content=str(h.payload.get("content", "")),
            score=float(h.score),
            path=str(h.payload.get("file_path", "")),
            symbol=str(h.payload.get("symbol", "")),
            start_line=int(h.payload.get("start_line", 0)),
            end_line=int(h.payload.get("end_line", 0)),
        )
        for h in response.points
        if h.payload
    ]


async def load_corpus(qdrant: AsyncQdrantClient) -> list[RetrievalResult]:
    """Load every chunk from Qdrant for in-memory BM25 indexing."""
    results: list[RetrievalResult] = []
    offset: Any = None
    while True:
        points, offset = await qdrant.scroll(
            collection_name=COLLECTION_NAME,
            with_payload=True,
            limit=1000,
            offset=offset,
        )
        for p in points:
            if p.payload:
                results.append(
                    RetrievalResult(
                        content=str(p.payload.get("content", "")),
                        score=0.0,
                        path=str(p.payload.get("file_path", "")),
                        symbol=str(p.payload.get("symbol", "")),
                        start_line=int(p.payload.get("start_line", 0)),
                        end_line=int(p.payload.get("end_line", 0)),
                    )
                )
        if offset is None:
            break
    return results
