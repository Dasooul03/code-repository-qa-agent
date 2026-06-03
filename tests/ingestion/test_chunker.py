"""Tests for src/ingestion/chunker.py."""

from pathlib import Path

from src.ingestion.chunker import chunk_parse_result
from src.ingestion.parser import parse_file

_PYTHON_SRC = """\
def add(a: int, b: int) -> int:
    return a + b


class Calculator:
    def multiply(self, a: int, b: int) -> int:
        return a * b
"""

_MODULE_ONLY_SRC = """\
X = 1
Y = 2
"""

_JAVA_SRC = """\
public class Calc {
    public int add(int a, int b) {
        return a + b;
    }
}
"""


def test_python_chunks_contain_function_and_class(tmp_path: Path) -> None:
    f = tmp_path / "calc.py"
    f.write_text(_PYTHON_SRC)
    result = parse_file(f)
    assert result is not None
    chunks = chunk_parse_result(result)
    symbols = {c.symbol for c in chunks}
    assert "add" in symbols
    assert "Calculator" in symbols


def test_chunks_have_valid_line_numbers(tmp_path: Path) -> None:
    f = tmp_path / "calc.py"
    f.write_text(_PYTHON_SRC)
    result = parse_file(f)
    assert result is not None
    for chunk in chunk_parse_result(result):
        assert chunk.start_line >= 1
        assert chunk.end_line >= chunk.start_line
        assert chunk.file_path == str(f)


def test_module_fallback_when_no_functions_or_classes(tmp_path: Path) -> None:
    f = tmp_path / "consts.py"
    f.write_text(_MODULE_ONLY_SRC)
    result = parse_file(f)
    assert result is not None
    chunks = chunk_parse_result(result)
    assert len(chunks) == 1
    assert chunks[0].chunk_type == "module"
    assert chunks[0].symbol == "<module>"


def test_chunk_content_is_non_empty(tmp_path: Path) -> None:
    f = tmp_path / "calc.py"
    f.write_text(_PYTHON_SRC)
    result = parse_file(f)
    assert result is not None
    for chunk in chunk_parse_result(result):
        assert chunk.content.strip() != ""


def test_java_chunks_contain_class_and_method(tmp_path: Path) -> None:
    f = tmp_path / "Calc.java"
    f.write_text(_JAVA_SRC)
    result = parse_file(f)
    assert result is not None
    chunks = chunk_parse_result(result)
    types = {c.chunk_type for c in chunks}
    assert "class" in types or "function" in types
