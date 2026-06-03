"""Tests for symbol MCP tools."""

from pathlib import Path

from src.mcp.symbol.tools import find_definition, find_references, find_symbol


def test_find_symbol_locates_function(tmp_path: Path) -> None:
    (tmp_path / "auth.py").write_text("def login(user, pwd):\n    pass\n")
    result = find_symbol("login", str(tmp_path))
    assert len(result["definitions"]) == 1
    assert result["definitions"][0]["kind"] == "function"
    assert result["definitions"][0]["line"] == 1


def test_find_symbol_locates_class(tmp_path: Path) -> None:
    (tmp_path / "models.py").write_text("class User:\n    pass\n")
    result = find_symbol("User", str(tmp_path))
    assert any(d["kind"] == "class" for d in result["definitions"])


def test_find_symbol_not_found(tmp_path: Path) -> None:
    (tmp_path / "empty.py").write_text("")
    result = find_symbol("NonExistent", str(tmp_path))
    assert result["definitions"] == []


def test_find_references_finds_usages(tmp_path: Path) -> None:
    (tmp_path / "caller.py").write_text("from auth import login\nlogin(u, p)\n")
    result = find_references("login", str(tmp_path))
    assert len(result["references"]) == 2
    assert all(r["file"] == "caller.py" for r in result["references"])


def test_find_definition_returns_full_source(tmp_path: Path) -> None:
    src = "def greet(name):\n    return f'Hello {name}'\n"
    (tmp_path / "greet.py").write_text(src)
    result = find_definition("greet", str(tmp_path))
    assert result["symbol"] == "greet"
    assert result["start_line"] == 1
    assert "Hello" in result["source"]


def test_find_definition_not_found(tmp_path: Path) -> None:
    (tmp_path / "empty.py").write_text("")
    result = find_definition("ghost", str(tmp_path))
    assert "error" in result
