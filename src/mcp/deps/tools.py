"""Dependency MCP tool implementations."""

import ast
import re
from pathlib import Path
from typing import Any


def dependency_graph(repo_root: str) -> dict[str, Any]:
    """Build a module-level import dependency graph for the repository.

    Walks all Python files and collects top-level import statements to produce
    a mapping from each file to its list of imported modules.

    Args:
        repo_root: Absolute path to the repository root.

    Returns:
        Dict with keys: graph (dict mapping relative path → list[str]).
    """
    repo = Path(repo_root)
    graph: dict[str, list[str]] = {}

    for file_path in sorted(repo.rglob("*.py")):
        if any(p.startswith(".") for p in file_path.parts):
            continue
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)
        except (OSError, SyntaxError):
            continue

        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split(".")[0])

        rel = str(file_path.relative_to(repo))
        graph[rel] = sorted(set(imports))

    return {"graph": graph}


def package_info(repo_root: str) -> dict[str, Any]:
    """Extract package metadata and dependencies from pyproject.toml or requirements.txt."""  # noqa: E501
    repo = Path(repo_root)

    # Prefer pyproject.toml
    pyproject = repo / "pyproject.toml"
    if pyproject.is_file():
        return _parse_pyproject(pyproject)

    # Fall back to requirements.txt
    requirements = repo / "requirements.txt"
    if requirements.is_file():
        return _parse_requirements(requirements)

    return {"error": "No pyproject.toml or requirements.txt found", "source": None}


def _parse_pyproject(path: Path) -> dict[str, Any]:
    """Parse pyproject.toml for project name, version, and dependencies."""
    content = path.read_text(encoding="utf-8")

    name_match = re.search(r'^name\s*=\s*"([^"]+)"', content, re.MULTILINE)
    version_match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)

    # Extract the [project.dependencies] block
    deps_match = re.search(
        r"^dependencies\s*=\s*\[(.*?)\]", content, re.MULTILINE | re.DOTALL
    )
    deps: list[str] = []
    if deps_match:
        raw = deps_match.group(1)
        for line in raw.splitlines():
            line = line.strip().strip('",').strip()
            if line:
                deps.append(line)

    return {
        "source": "pyproject.toml",
        "name": name_match.group(1) if name_match else None,
        "version": version_match.group(1) if version_match else None,
        "dependencies": deps,
    }


def _parse_requirements(path: Path) -> dict[str, Any]:
    """Parse requirements.txt for dependencies."""
    deps: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("-"):
            deps.append(line)
    return {
        "source": "requirements.txt",
        "name": None,
        "version": None,
        "dependencies": deps,
    }
