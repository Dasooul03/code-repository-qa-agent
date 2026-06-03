"""Symbol MCP tool implementations."""

import ast
import re
from pathlib import Path
from typing import Any

_PY_SYMBOL_TYPES = frozenset(
    ["function_definition", "class_definition", "async_function_def"]
)


def find_symbol(
    symbol: str,
    repo_root: str,
    language: str = "python",
) -> dict[str, Any]:
    """Find where a symbol (function, class, variable) is defined.

    Searches Python files for `def <symbol>`, `class <symbol>`, or assignment.

    Args:
        symbol: Symbol name to look up.
        repo_root: Absolute path to the repository root.
        language: Currently only 'python' is supported.

    Returns:
        Dict with keys: symbol, definitions (list of file/line/kind dicts).
    """
    repo = Path(repo_root)
    definitions: list[dict[str, Any]] = []

    def_pattern = re.compile(
        r"^\s*(?:(async\s+)?def|class)\s+" + re.escape(symbol) + r"\b"
    )
    assign_pattern = re.compile(r"^\s*" + re.escape(symbol) + r"\s*=")

    for file_path in sorted(repo.rglob("*.py")):
        if any(p.startswith(".") for p in file_path.parts):
            continue
        try:
            lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if def_pattern.match(line):
                kind = "class" if "class" in line.split()[0:2] else "function"
                definitions.append(
                    {
                        "file": str(file_path.relative_to(repo)),
                        "line": i,
                        "kind": kind,
                        "text": line.strip(),
                    }
                )
            elif assign_pattern.match(line) and not definitions:
                definitions.append(
                    {
                        "file": str(file_path.relative_to(repo)),
                        "line": i,
                        "kind": "variable",
                        "text": line.strip(),
                    }
                )

    return {"symbol": symbol, "definitions": definitions[:20]}


def find_references(
    symbol: str,
    repo_root: str,
) -> dict[str, Any]:
    """Find all call sites and usages of a symbol across the repository.

    Args:
        symbol: Symbol name to search for.
        repo_root: Absolute path to the repository root.

    Returns:
        Dict with keys: symbol, references (list of file/line/text dicts).
    """
    repo = Path(repo_root)
    pattern = re.compile(r"\b" + re.escape(symbol) + r"\b")
    references: list[dict[str, Any]] = []

    for file_path in sorted(repo.rglob("*.py")):
        if any(p.startswith(".") for p in file_path.parts):
            continue
        try:
            lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if pattern.search(line):
                references.append(
                    {
                        "file": str(file_path.relative_to(repo)),
                        "line": i,
                        "text": line.strip(),
                    }
                )

    return {"symbol": symbol, "references": references[:50]}


def find_definition(
    symbol: str,
    repo_root: str,
) -> dict[str, Any]:
    """Return the full source block of the first matching definition.

    Parses the AST to extract the complete function or class body.

    Args:
        symbol: Symbol name to look up.
        repo_root: Absolute path to the repository root.

    Returns:
        Dict with keys: symbol, file, start_line, end_line, source, or error.
    """
    repo = Path(repo_root)

    for file_path in sorted(repo.rglob("*.py")):
        if any(p.startswith(".") for p in file_path.parts):
            continue
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError):
            continue

        lines = source.splitlines()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == symbol:
                    start = node.lineno
                    end = node.end_lineno or start
                    snippet = "\n".join(lines[start - 1 : end])
                    return {
                        "symbol": symbol,
                        "file": str(file_path.relative_to(repo)),
                        "start_line": start,
                        "end_line": end,
                        "source": snippet,
                    }

    return {"error": f"Definition not found for symbol: {symbol}", "symbol": symbol}
