"""Tool implementations for the agent executor."""

import re
import subprocess
from dataclasses import asdict
from pathlib import Path
from typing import Any

from src.retrieval.hybrid_retriever import HybridRetriever


async def retriever_tool(
    query: str, retriever: HybridRetriever, top_k: int = 5
) -> list[dict[str, Any]]:
    """Retrieve code chunks relevant to the query."""
    results = await retriever.retrieve(query, top_k=top_k)
    return [asdict(r) for r in results]


def filesystem_tool(path: str, repo_root: str) -> dict[str, Any]:
    """Read a file from the repository."""
    full = Path(repo_root) / path
    if not full.is_file():
        return {"error": f"File not found: {path}", "path": path}
    content = full.read_text(encoding="utf-8", errors="replace")
    return {"path": path, "content": content, "line_count": len(content.splitlines())}


def git_tool(
    repo_root: str,
    operation: str = "log",
    target: str = "",
    n: int = 10,
) -> dict[str, Any]:
    """Run a read-only git query against the repository."""
    if operation == "log":
        cmd = ["git", "-C", repo_root, "log", "--oneline", f"-{n}"]
        if target:
            cmd += ["--", target]
    elif operation == "blame":
        if not target:
            return {"error": "blame requires a file path"}
        cmd = ["git", "-C", repo_root, "blame", target]
    elif operation == "diff":
        cmd = ["git", "-C", repo_root, "diff", "HEAD~1", "HEAD"]
        if target:
            cmd += ["--", target]
    else:
        return {"error": f"Unknown operation: {operation}"}

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return {"operation": operation, "output": proc.stdout.strip(), "target": target}
    except subprocess.TimeoutExpired:
        return {"error": "git operation timed out", "operation": operation}


def symbol_tool(symbol_name: str, repo_root: str) -> dict[str, Any]:
    """Search for occurrences of a symbol name across Python files."""
    pattern = re.compile(r"\b" + re.escape(symbol_name) + r"\b")
    matches: list[dict[str, Any]] = []
    repo = Path(repo_root)
    for file_path in repo.rglob("*.py"):
        if ".git" in file_path.parts or ".venv" in file_path.parts:
            continue
        try:
            lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    matches.append(
                        {
                            "file": str(file_path.relative_to(repo)),
                            "line": i,
                            "text": line.strip(),
                        }
                    )
        except OSError:
            continue
    return {"symbol": symbol_name, "matches": matches[:20]}
