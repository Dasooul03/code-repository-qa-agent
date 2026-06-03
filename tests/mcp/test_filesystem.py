"""Tests for filesystem MCP tools."""

from pathlib import Path

from src.mcp.filesystem.tools import list_dir, read_file, search_file


def test_read_file_returns_content(tmp_path: Path) -> None:
    f = tmp_path / "hello.py"
    f.write_text("print('hello')")
    result = read_file("hello.py", str(tmp_path))
    assert result["content"] == "print('hello')"
    assert result["line_count"] == 1
    assert result["path"] == "hello.py"


def test_read_file_missing_returns_error(tmp_path: Path) -> None:
    result = read_file("nope.py", str(tmp_path))
    assert "error" in result


def test_list_dir_returns_entries(tmp_path: Path) -> None:
    (tmp_path / "foo.py").write_text("")
    (tmp_path / "bar").mkdir()
    result = list_dir("", str(tmp_path))
    names = [e["name"] for e in result["entries"]]
    assert "foo.py" in names
    assert "bar" in names


def test_list_dir_missing_returns_error(tmp_path: Path) -> None:
    result = list_dir("no_such_dir", str(tmp_path))
    assert "error" in result


def test_list_dir_excludes_hidden(tmp_path: Path) -> None:
    (tmp_path / ".hidden").mkdir()
    (tmp_path / "visible.py").write_text("")
    result = list_dir("", str(tmp_path))
    names = [e["name"] for e in result["entries"]]
    assert ".hidden" not in names
    assert "visible.py" in names


def test_search_file_by_substring(tmp_path: Path) -> None:
    (tmp_path / "auth.py").write_text("")
    (tmp_path / "main.py").write_text("")
    result = search_file("auth", str(tmp_path))
    assert "auth.py" in result["matches"]
    assert "main.py" not in result["matches"]


def test_search_file_no_match(tmp_path: Path) -> None:
    (tmp_path / "foo.py").write_text("")
    result = search_file("zzz_not_found", str(tmp_path))
    assert result["matches"] == []
