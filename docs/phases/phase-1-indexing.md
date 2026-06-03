# Phase 1: Code Indexing

**Commit:** `2594106 feat(phase-1): implement repository indexing pipeline`
**Date:** 2026-06-03
**Agent:** Claude (claude-sonnet-4-6)
**Status:** COMPLETE

## Goal

Implement the full code indexing pipeline: parse → chunk → embed → upsert into Qdrant with SHA256 incremental updates.

## Files Created

| File | Purpose |
|------|---------|
| `src/ingestion/parser.py` | tree-sitter multi-language parser (Python/Java/C++/JS/TS/TSX) |
| `src/ingestion/chunker.py` | AST-aware chunking by function/class/module |
| `src/ingestion/symbol_extractor.py` | Extract function/class/method/import symbols |
| `src/ingestion/indexer.py` | Full async pipeline with SHA256 incremental upsert |
| `tests/ingestion/test_parser.py` | Parser tests |
| `tests/ingestion/test_chunker.py` | Chunker tests |
| `tests/ingestion/test_symbol_extractor.py` | Symbol extractor tests |
| `tests/ingestion/test_indexer.py` | Indexer tests with mocked Qdrant + OpenAI |

## Key Implementation Details

### parser.py
```python
EXTENSION_TO_LANGUAGE = {".py": "python", ".java": "java", ...}
_LANGUAGES = {
    "python": Language(tspython.language()),
    "typescript": Language(tstypescript.language_typescript()),
    "tsx": Language(tstypescript.language_tsx()),
}
_PARSERS = {name: Parser(lang) for name, lang in _LANGUAGES.items()}
```
- `Parser(language)` constructor — tree-sitter 0.23+ API
- Language bindings have proper stubs; no `# type: ignore` needed

### chunker.py — always-descending DFS
```python
def collect_nodes(root: Node, target_types: frozenset[str]) -> list[Node]:
    stack: list[Node] = [root]
    while stack:
        node = stack.pop()
        if node.type in target_types:
            results.append(node)
        stack.extend(reversed(node.children))  # always recurse into children
```
Descending unconditionally ensures nested classes/functions are all captured.

### symbol_extractor.py — ancestor chain walk for method detection
```python
def _has_class_ancestor(node: Node, class_types: frozenset[str]) -> bool:
    parent = node.parent
    while parent is not None:
        if parent.type in class_types:
            return True
        parent = parent.parent
    return False
```
Python AST structure is `class_definition → block → function_definition` (not direct parent), so the ancestor chain walk is required.

### indexer.py — incremental SHA256 updates
```python
COLLECTION_NAME = "code_chunks"
VECTOR_SIZE = 3072   # text-embedding-3-large
BATCH_SIZE = 64

# Per-file: if sha matches stored → skip; else delete old chunks + upsert new
async def index_repository(repo_path: str | Path) -> None: ...

def _chunk_id(chunk: Chunk) -> str:
    key = f"{chunk.file_path}:{chunk.start_line}:{chunk.end_line}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, key))
```

## Bugs Fixed During Validation

| Error | Fix |
|-------|-----|
| `KeywordIndexParams` arg-type | Changed `field_schema="keyword"` → `field_schema=KeywordIndexParams(type=KeywordIndexType.KEYWORD)` |
| `scroll` offset type error | Changed `offset: str \| int \| None = None` → `offset: Any = None` (qdrant returns `PointId` union) |
| `zip()` without `strict=` (B905) | Added `strict=True` to `zip(batch, vectors, strict=True)` |
| `_has_class_ancestor` test failure | Rewrote from direct-parent check to full ancestor chain walk |

## Commands Run

```
uv sync --all-groups
uv run black src tests    → reformatted 8 files
uv run ruff check --fix   → 9 issues auto-fixed
uv run mypy src tests     → success
uv run pytest             → 37/37 passed
git commit 2594106
```

## Validation

- black: ✓ | ruff: ✓ | mypy: ✓ | pytest: 37/37 ✓

## Next Phase

Phase 2 — Hybrid Retrieval
