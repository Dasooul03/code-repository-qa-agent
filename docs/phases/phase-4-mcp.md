# Phase 4: MCP Tools

**Commit:** `a00e3e3 feat(phase-4): implement mcp tools`
**Date:** 2026-06-03
**Agent:** Claude (claude-sonnet-4-6)
**Status:** COMPLETE

## Goal

Implement 11 MCP-backed tool functions across four domains and wrap them as LangChain `StructuredTool` instances via `MCPToolAdapter`.

## Files Created

| File | Purpose |
|------|---------|
| `src/mcp/filesystem/tools.py` | `read_file`, `list_dir`, `search_file` |
| `src/mcp/git/tools.py` | `git_log`, `git_blame`, `git_diff` |
| `src/mcp/symbol/tools.py` | `find_symbol`, `find_references`, `find_definition` |
| `src/mcp/deps/tools.py` | `dependency_graph`, `package_info` |
| `src/mcp/adapter.py` | `MCPToolAdapter` + 11 Pydantic input schemas |
| `tests/mcp/test_filesystem.py` | 7 tests for filesystem tools |
| `tests/mcp/test_git.py` | 6 tests for git tools (mocked subprocess) |
| `tests/mcp/test_symbol.py` | 6 tests for symbol tools |
| `tests/mcp/test_deps.py` | 5 tests for dependency tools |
| `tests/mcp/test_adapter.py` | 5 tests for MCPToolAdapter |

## Tool Inventory

### Filesystem
- `read_file(path, repo_root)` → `{path, content, line_count}` or `{error}`
- `list_dir(path, repo_root)` → `{path, entries: [{name, type, size}]}`
- `search_file(pattern, repo_root)` → `{pattern, matches: [rel_path, ...]}`

### Git
- `git_log(repo_root, path, n, since, author)` → `{commits: [{hash, author, email, date, subject}]}`
- `git_blame(repo_root, path)` → `{path, lines: [{line_no, hash, author, date, content}]}`
- `git_diff(repo_root, path, ref_a, ref_b)` → `{ref_a, ref_b, path, diff}`

### Symbol
- `find_symbol(symbol, repo_root)` → `{symbol, definitions: [{file, line, kind, text}]}`
- `find_references(symbol, repo_root)` → `{symbol, references: [{file, line, text}]}`
- `find_definition(symbol, repo_root)` → `{symbol, file, start_line, end_line, source}` (full AST-extracted body)

### Dependencies
- `dependency_graph(repo_root)` → `{graph: {rel_path → [module, ...]}}`
- `package_info(repo_root)` → `{source, name, version, dependencies: [str]}`

## MCPToolAdapter Design

```python
class MCPToolAdapter:
    def __init__(self, repo_root: str) -> None: ...

    def _bind(self, fn, **fixed) -> Callable:
        # partial-applies repo_root so LangChain doesn't see it as an arg

    def get_tools(self) -> list[StructuredTool]:
        # returns 11 StructuredTool instances, each with Pydantic input schema
```

Each tool's input schema is a `BaseModel` subclass. `repo_root` is injected via `_bind()` so the LLM only sees domain-relevant parameters.

## Key Implementation Decisions

| Decision | Reason |
|----------|--------|
| `find_definition` uses `ast.parse` | tree-sitter not needed here; stdlib `ast` gives exact `lineno`/`end_lineno` |
| `git blame --line-porcelain` | Machine-readable format with per-commit metadata before each line |
| `_build_bm25` None guard pattern reused | Consistent with Phase 2 — empty corpus guard prevents ZeroDivisionError |
| Pydantic input schemas per tool | LangChain `StructuredTool` requires `args_schema`; enables LLM structured calls |

## Bugs Fixed During Validation

| Error | Fix |
|-------|-----|
| `E501` on long `description=` strings | Added `# noqa: E501` (string literals inside fn calls can't be wrapped) |
| Unused `subprocess` import in deps/tools.py | Removed (ruff --fix) |
| Broken docstring after inline conversion | Rewrote to single-line `"""..."""` format |

## Commands Run

```
uv run black src/mcp tests/mcp   → 3 files reformatted
uv run ruff check --fix          → auto-fixed imports; manual noqa for E501
uv run mypy src/mcp tests/mcp    → success (16 source files)
uv run pytest tests/mcp -v       → 29/29 passed
uv run pytest -v                 → 88/88 passed (no regressions)
git commit a00e3e3
```

## Validation

- black: ✓ | ruff: ✓ | mypy: ✓ | pytest: 88/88 ✓

## Next Phase

Phase 5 — FastAPI API (`POST /chat`, `POST /repo/register`, `GET /session/{id}`, SSE streaming)
