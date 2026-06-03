"""Repository indexing pipeline: parse → chunk → embed → Qdrant."""

import hashlib
import logging
import uuid
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    KeywordIndexParams,
    KeywordIndexType,
    MatchValue,
    PointStruct,
    VectorParams,
)

from src.config import get_settings
from src.ingestion.chunker import Chunk, chunk_parse_result
from src.ingestion.parser import get_supported_extensions, parse_file

logger = logging.getLogger(__name__)

COLLECTION_NAME = "code_chunks"
VECTOR_SIZE = 3072  # text-embedding-3-large
BATCH_SIZE = 64


async def ensure_collection(client: AsyncQdrantClient) -> None:
    """Create the Qdrant collection and payload index if they do not exist."""
    existing = {c.name for c in (await client.get_collections()).collections}
    if COLLECTION_NAME not in existing:
        await client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        await client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="file_path",
            field_schema=KeywordIndexParams(type=KeywordIndexType.KEYWORD),
        )


async def _get_indexed_file_shas(
    client: AsyncQdrantClient,
) -> dict[str, str]:
    """Return a mapping of file_path -> file_sha256 for all indexed chunks."""
    result: dict[str, str] = {}
    offset: Any = None
    while True:
        points, offset = await client.scroll(
            collection_name=COLLECTION_NAME,
            with_payload=["file_path", "file_sha256"],
            limit=1000,
            offset=offset,
        )
        for p in points:
            if p.payload and "file_path" in p.payload and "file_sha256" in p.payload:
                result[str(p.payload["file_path"])] = str(p.payload["file_sha256"])
        if offset is None:
            break
    return result


async def _embed_texts(client: AsyncOpenAI, texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts using text-embedding-3-large."""
    settings = get_settings()
    response = await client.embeddings.create(
        input=texts,
        model=settings.embedding_model,
    )
    return [item.embedding for item in response.data]


def _chunk_id(chunk: Chunk) -> str:
    """Return a deterministic UUID string for a chunk."""
    key = f"{chunk.file_path}:{chunk.start_line}:{chunk.end_line}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, key))


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


async def _upsert_chunks(
    qdrant: AsyncQdrantClient,
    openai_client: AsyncOpenAI,
    chunks: list[Chunk],
    file_sha: str,
) -> None:
    """Embed and upsert chunks into Qdrant in batches."""
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        vectors = await _embed_texts(openai_client, [c.content for c in batch])
        points = [
            PointStruct(
                id=_chunk_id(chunk),
                vector=vec,
                payload={
                    "content": chunk.content,
                    "symbol": chunk.symbol,
                    "file_path": chunk.file_path,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "chunk_type": chunk.chunk_type,
                    "file_sha256": file_sha,
                },
            )
            for chunk, vec in zip(batch, vectors, strict=True)
        ]
        await qdrant.upsert(collection_name=COLLECTION_NAME, points=points)


async def index_repository(repo_path: str | Path) -> None:
    """Index all supported source files in a repository directory."""
    settings = get_settings()
    repo = Path(repo_path)

    qdrant = AsyncQdrantClient(url=settings.qdrant_url)
    openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

    await ensure_collection(qdrant)
    indexed = await _get_indexed_file_shas(qdrant)

    supported = get_supported_extensions()
    files = [
        f
        for f in repo.rglob("*")
        if f.is_file() and f.suffix.lower() in supported and ".git" not in f.parts
    ]

    logger.info("Found %d source files in %s", len(files), repo)

    for file_path in files:
        sha = _file_sha256(file_path)
        if indexed.get(str(file_path)) == sha:
            logger.debug("Skipping unchanged file: %s", file_path)
            continue

        # Delete stale chunks if the file content changed
        if str(file_path) in indexed:
            await qdrant.delete(
                collection_name=COLLECTION_NAME,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="file_path",
                            match=MatchValue(value=str(file_path)),
                        )
                    ]
                ),
            )

        parse_result = parse_file(file_path)
        if parse_result is None:
            continue

        chunks = chunk_parse_result(parse_result)
        if not chunks:
            continue

        await _upsert_chunks(qdrant, openai_client, chunks, sha)
        logger.info("Indexed %d chunks from %s", len(chunks), file_path)

    logger.info("Indexing complete.")
