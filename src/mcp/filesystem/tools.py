"""Filesystem MCP tool implementations."""

import re
from pathlib import Path
from typing import Any


def read_file(path: str, repo_root: str) -> dict[str, Any]:
    """Read a file's full content from the repository.

    Args:
        path: Relative file path within the repository.
        repo_root: Absolute path to the repository root.

    Returns:
        Dict with keys: path, content, line_count, or error.
    """
    full = Path(repo_root) / path
    if not full.is_file():
        return {"error": f"File not found: {path}", "path": path}
    content = full.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()
    return {"path": path, "content": content, "line_count": len(lines)}


def list_dir(path: str, repo_root: str) -> dict[str, Any]:
    """List entries in a directory within the repository.

    Args:
        path: Relative directory path ('' or '.' for root).
        repo_root: Absolute path to the repository root.

    Returns:
        Dict with keys: path, entries (list of dicts with name/type/size).
    """
    target = Path(repo_root) / path if path else Path(repo_root)
    if not target.is_dir():
        return {"error": f"Directory not found: {path}", "path": path}

    entries: list[dict[str, Any]] = []
    for item in sorted(target.iterdir()):
        if item.name.startswith("."):
            continue
        entries.append(
            {
                "name": item.name,
                "type": "dir" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None,
            }
        )
    return {"path": path or ".", "entries": entries}


def search_file(pattern: str, repo_root: str, glob: str = "**/*") -> dict[str, Any]:
    """Search for files matching a glob pattern or containing a text pattern.

    If pattern looks like a glob (contains * or ?), matches file paths.
    Otherwise, performs a case-insensitive substring search in file names.

    Args:
        pattern: Glob pattern or substring to search for.
        repo_root: Absolute path to the repository root.
        glob: Glob to restrict the file search scope.

    Returns:
        Dict with keys: pattern, matches (list of relative paths).
    """
    repo = Path(repo_root)
    is_glob = "*" in pattern or "?" in pattern

    matches: list[str] = []
    for file_path in sorted(repo.glob(glob)):
        if not file_path.is_file():
            continue
        rel = str(file_path.relative_to(repo))
        if any(part.startswith(".") for part in file_path.parts):
            continue
        if is_glob:
            if re.fullmatch(pattern.replace("*", ".*").replace("?", "."), rel):
                matches.append(rel)
        else:
            if pattern.lower() in file_path.name.lower():
                matches.append(rel)

    return {"pattern": pattern, "matches": matches[:50]}
