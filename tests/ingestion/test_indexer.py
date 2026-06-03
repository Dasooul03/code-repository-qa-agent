"""Tests for src/ingestion/indexer.py."""

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from src.ingestion.indexer import index_repository


async def test_index_repository_creates_collection_and_upserts(
    tmp_path: Path,
) -> None:
    (tmp_path / "hello.py").write_text("def hello(): pass\n")

    mock_qdrant: Any = AsyncMock()
    mock_qdrant.get_collections.return_value = MagicMock(collections=[])
    mock_qdrant.scroll.return_value = ([], None)

    mock_openai: Any = AsyncMock()
    fake_emb: Any = MagicMock()
    fake_emb.embedding = [0.0] * 3072
    mock_openai.embeddings.create.return_value = MagicMock(data=[fake_emb])

    with (
        patch("src.ingestion.indexer.AsyncQdrantClient", return_value=mock_qdrant),
        patch("src.ingestion.indexer.AsyncOpenAI", return_value=mock_openai),
    ):
        await index_repository(tmp_path)

    mock_qdrant.create_collection.assert_called_once()
    mock_qdrant.upsert.assert_called()


async def test_index_repository_skips_unchanged_files(tmp_path: Path) -> None:
    py_file = tmp_path / "stable.py"
    py_file.write_text("x = 1\n")

    import hashlib

    sha = hashlib.sha256(py_file.read_bytes()).hexdigest()

    # Qdrant reports this file is already indexed with the same SHA
    mock_qdrant: Any = AsyncMock()
    mock_qdrant.get_collections.return_value = MagicMock(
        collections=[MagicMock(name="code_chunks")]
    )
    mock_scroll_point: Any = MagicMock()
    mock_scroll_point.payload = {
        "file_path": str(py_file),
        "file_sha256": sha,
    }
    mock_qdrant.scroll.return_value = ([mock_scroll_point], None)

    mock_openai: Any = AsyncMock()

    with (
        patch("src.ingestion.indexer.AsyncQdrantClient", return_value=mock_qdrant),
        patch("src.ingestion.indexer.AsyncOpenAI", return_value=mock_openai),
    ):
        await index_repository(tmp_path)

    mock_qdrant.upsert.assert_not_called()


async def test_index_repository_renames_stale_file(tmp_path: Path) -> None:
    py_file = tmp_path / "changed.py"
    py_file.write_text("def foo(): pass\n")

    mock_qdrant: Any = AsyncMock()
    mock_qdrant.get_collections.return_value = MagicMock(
        collections=[MagicMock(name="code_chunks")]
    )
    # Report an old (different) SHA for this file
    mock_scroll_point: Any = MagicMock()
    mock_scroll_point.payload = {
        "file_path": str(py_file),
        "file_sha256": "old_sha",
    }
    mock_qdrant.scroll.return_value = ([mock_scroll_point], None)

    mock_openai: Any = AsyncMock()
    fake_emb: Any = MagicMock()
    fake_emb.embedding = [0.0] * 3072
    mock_openai.embeddings.create.return_value = MagicMock(data=[fake_emb])

    with (
        patch("src.ingestion.indexer.AsyncQdrantClient", return_value=mock_qdrant),
        patch("src.ingestion.indexer.AsyncOpenAI", return_value=mock_openai),
    ):
        await index_repository(tmp_path)

    # Old chunks must be deleted before re-indexing
    mock_qdrant.delete.assert_called_once()
    mock_qdrant.upsert.assert_called()
