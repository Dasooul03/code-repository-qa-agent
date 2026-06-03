"""Tests for MCPToolAdapter."""

from pathlib import Path

from langchain_core.tools import StructuredTool
from src.mcp.adapter import MCPToolAdapter


def test_adapter_returns_all_tools(tmp_path: Path) -> None:
    adapter = MCPToolAdapter(str(tmp_path))
    tools = adapter.get_tools()
    assert len(tools) == 11


def test_adapter_all_tools_are_structured(tmp_path: Path) -> None:
    adapter = MCPToolAdapter(str(tmp_path))
    for tool in adapter.get_tools():
        assert isinstance(tool, StructuredTool)


def test_adapter_tool_names(tmp_path: Path) -> None:
    adapter = MCPToolAdapter(str(tmp_path))
    names = {t.name for t in adapter.get_tools()}
    expected = {
        "read_file",
        "list_dir",
        "search_file",
        "git_log",
        "git_blame",
        "git_diff",
        "find_symbol",
        "find_references",
        "find_definition",
        "dependency_graph",
        "package_info",
    }
    assert names == expected


def test_adapter_read_file_tool_works(tmp_path: Path) -> None:
    (tmp_path / "hello.py").write_text("x = 1")
    adapter = MCPToolAdapter(str(tmp_path))
    tool = next(t for t in adapter.get_tools() if t.name == "read_file")
    result = tool.invoke({"path": "hello.py"})
    assert isinstance(result, dict)
    assert result["content"] == "x = 1"


def test_adapter_package_info_tool_works(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "test"\nversion = "1.0"\ndependencies = []\n'
    )
    adapter = MCPToolAdapter(str(tmp_path))
    tool = next(t for t in adapter.get_tools() if t.name == "package_info")
    result = tool.invoke({})
    assert result["name"] == "test"
