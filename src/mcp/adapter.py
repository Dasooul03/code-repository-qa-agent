"""MCPToolAdapter: converts MCP tool functions into LangChain StructuredTools."""

from collections.abc import Callable
from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from src.mcp.deps.tools import dependency_graph, package_info
from src.mcp.filesystem.tools import list_dir, read_file, search_file
from src.mcp.git.tools import git_blame, git_diff, git_log
from src.mcp.symbol.tools import find_definition, find_references, find_symbol

# ---------------------------------------------------------------------------
# Input schemas (Pydantic v2)
# ---------------------------------------------------------------------------


class ReadFileInput(BaseModel):
    path: str = Field(description="Relative file path within the repository")


class ListDirInput(BaseModel):
    path: str = Field(default="", description="Relative directory path ('' for root)")


class SearchFileInput(BaseModel):
    pattern: str = Field(description="Glob pattern or filename substring to search")


class GitLogInput(BaseModel):
    path: str = Field(default="", description="Optional file path to scope the log")
    n: int = Field(default=20, description="Maximum number of commits to return")
    since: str = Field(default="", description="Optional ISO date filter (YYYY-MM-DD)")
    author: str = Field(default="", description="Optional author name/email filter")


class GitBlameInput(BaseModel):
    path: str = Field(description="Relative file path to blame")


class GitDiffInput(BaseModel):
    path: str = Field(default="", description="Optional file path to scope the diff")
    ref_a: str = Field(default="HEAD~1", description="Base ref")
    ref_b: str = Field(default="HEAD", description="Target ref")


class FindSymbolInput(BaseModel):
    symbol: str = Field(description="Symbol name (function, class, variable)")


class FindReferencesInput(BaseModel):
    symbol: str = Field(description="Symbol name to find usages of")


class FindDefinitionInput(BaseModel):
    symbol: str = Field(description="Symbol name to retrieve full source for")


class DependencyGraphInput(BaseModel):
    pass  # no extra params; uses repo_root from adapter


class PackageInfoInput(BaseModel):
    pass  # no extra params; uses repo_root from adapter


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


class MCPToolAdapter:
    """Wraps MCP tool functions as LangChain StructuredTool instances.

    Each tool function is partially applied with the repo_root so callers
    do not need to pass it explicitly.

    Example:
        adapter = MCPToolAdapter(repo_root="/path/to/repo")
        tools = adapter.get_tools()  # list of StructuredTool
    """

    def __init__(self, repo_root: str) -> None:
        self._root = repo_root

    def _bind(self, fn: Callable[..., Any], **fixed: Any) -> Callable[..., Any]:
        """Return a wrapper that injects fixed keyword arguments into fn."""

        def bound(**kwargs: Any) -> Any:
            return fn(**fixed, **kwargs)

        return bound

    def get_tools(self) -> list[StructuredTool]:
        """Return all MCP tools as LangChain StructuredTool instances."""
        root = self._root
        return [
            StructuredTool.from_function(
                func=self._bind(read_file, repo_root=root),
                name="read_file",
                description="Read the full content of a file in the repository.",
                args_schema=ReadFileInput,
            ),
            StructuredTool.from_function(
                func=self._bind(list_dir, repo_root=root),
                name="list_dir",
                description="List files and subdirectories in a repository directory.",
                args_schema=ListDirInput,
            ),
            StructuredTool.from_function(
                func=self._bind(search_file, repo_root=root),
                name="search_file",
                description="Search for files by name or glob pattern.",
                args_schema=SearchFileInput,
            ),
            StructuredTool.from_function(
                func=self._bind(git_log, repo_root=root),
                name="git_log",
                description="Return git commit log, optionally scoped to a file or author.",  # noqa: E501
                args_schema=GitLogInput,
            ),
            StructuredTool.from_function(
                func=self._bind(git_blame, repo_root=root),
                name="git_blame",
                description="Return per-line blame showing who last modified each line.",  # noqa: E501
                args_schema=GitBlameInput,
            ),
            StructuredTool.from_function(
                func=self._bind(git_diff, repo_root=root),
                name="git_diff",
                description="Return the diff between two git refs, optionally for a file.",  # noqa: E501
                args_schema=GitDiffInput,
            ),
            StructuredTool.from_function(
                func=self._bind(find_symbol, repo_root=root),
                name="find_symbol",
                description="Find where a function, class, or variable is defined.",
                args_schema=FindSymbolInput,
            ),
            StructuredTool.from_function(
                func=self._bind(find_references, repo_root=root),
                name="find_references",
                description="Find all usages and call sites of a symbol in the codebase.",  # noqa: E501
                args_schema=FindReferencesInput,
            ),
            StructuredTool.from_function(
                func=self._bind(find_definition, repo_root=root),
                name="find_definition",
                description="Return complete source code of a function or class definition.",  # noqa: E501
                args_schema=FindDefinitionInput,
            ),
            StructuredTool.from_function(
                func=self._bind(dependency_graph, repo_root=root),
                name="dependency_graph",
                description="Build the module-level import dependency graph.",
                args_schema=DependencyGraphInput,
            ),
            StructuredTool.from_function(
                func=self._bind(package_info, repo_root=root),
                name="package_info",
                description="Extract package name, version, and dependencies from pyproject.toml.",  # noqa: E501
                args_schema=PackageInfoInput,
            ),
        ]
