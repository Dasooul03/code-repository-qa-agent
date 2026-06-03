"""Tests for src/ingestion/symbol_extractor.py."""

from pathlib import Path

from src.ingestion.parser import parse_file
from src.ingestion.symbol_extractor import extract_symbols

_PYTHON_SRC = """\
import os
from pathlib import Path


def login(user: str) -> bool:
    return True


class UserService:
    def get_user(self, uid: int) -> dict:  # type: ignore[type-arg]
        return {}
"""

_JS_SRC = """\
import React from 'react';

function App() {
    return null;
}

class MyComponent {
    render() {
        return null;
    }
}
"""


def test_extracts_top_level_function(tmp_path: Path) -> None:
    f = tmp_path / "auth.py"
    f.write_text(_PYTHON_SRC)
    result = parse_file(f)
    assert result is not None
    symbols = extract_symbols(result)
    names = {s.symbol for s in symbols}
    assert "login" in names


def test_extracts_class_symbol(tmp_path: Path) -> None:
    f = tmp_path / "svc.py"
    f.write_text(_PYTHON_SRC)
    result = parse_file(f)
    assert result is not None
    symbols = extract_symbols(result)
    classes = [s for s in symbols if s.type == "class"]
    assert any(s.symbol == "UserService" for s in classes)


def test_extracts_method_inside_class(tmp_path: Path) -> None:
    f = tmp_path / "svc.py"
    f.write_text(_PYTHON_SRC)
    result = parse_file(f)
    assert result is not None
    symbols = extract_symbols(result)
    methods = [s for s in symbols if s.type == "method"]
    assert any(s.symbol == "get_user" for s in methods)


def test_extracts_import_symbols(tmp_path: Path) -> None:
    f = tmp_path / "svc.py"
    f.write_text(_PYTHON_SRC)
    result = parse_file(f)
    assert result is not None
    symbols = extract_symbols(result)
    imports = [s for s in symbols if s.type == "import"]
    assert len(imports) >= 1


def test_symbol_line_numbers_are_positive(tmp_path: Path) -> None:
    f = tmp_path / "svc.py"
    f.write_text(_PYTHON_SRC)
    result = parse_file(f)
    assert result is not None
    for sym in extract_symbols(result):
        assert sym.start >= 1
        assert sym.end >= sym.start


def test_javascript_symbols(tmp_path: Path) -> None:
    f = tmp_path / "app.js"
    f.write_text(_JS_SRC)
    result = parse_file(f)
    assert result is not None
    symbols = extract_symbols(result)
    names = {s.symbol for s in symbols}
    assert "App" in names
