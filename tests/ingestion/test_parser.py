"""Tests for src/ingestion/parser.py."""

from pathlib import Path

from src.ingestion.parser import get_supported_extensions, parse_file

_PYTHON_SRC = """\
def hello(name: str) -> str:
    \"\"\"Say hello.\"\"\"
    return f"Hello, {name}"


class Greeter:
    def greet(self) -> str:
        return "hi"
"""

_JAVA_SRC = """\
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}
"""

_JS_SRC = """\
function greet(name) {
    return "Hello " + name;
}
"""


def test_parse_python_file(tmp_path: Path) -> None:
    f = tmp_path / "sample.py"
    f.write_text(_PYTHON_SRC)
    result = parse_file(f)
    assert result is not None
    assert result.language == "python"
    assert result.tree.root_node.type == "module"


def test_parse_java_file(tmp_path: Path) -> None:
    f = tmp_path / "Calculator.java"
    f.write_text(_JAVA_SRC)
    result = parse_file(f)
    assert result is not None
    assert result.language == "java"


def test_parse_javascript_file(tmp_path: Path) -> None:
    f = tmp_path / "app.js"
    f.write_text(_JS_SRC)
    result = parse_file(f)
    assert result is not None
    assert result.language == "javascript"


def test_parse_unsupported_returns_none(tmp_path: Path) -> None:
    f = tmp_path / "sample.rb"
    f.write_text('puts "hello"')
    assert parse_file(f) is None


def test_parse_ts_extension(tmp_path: Path) -> None:
    f = tmp_path / "app.ts"
    f.write_text("const x: number = 1;\n")
    result = parse_file(f)
    assert result is not None
    assert result.language == "typescript"


def test_supported_extensions_includes_common_types() -> None:
    exts = get_supported_extensions()
    for ext in (".py", ".java", ".cpp", ".js", ".ts", ".tsx"):
        assert ext in exts


def test_parse_result_stores_source(tmp_path: Path) -> None:
    f = tmp_path / "sample.py"
    f.write_text(_PYTHON_SRC)
    result = parse_file(f)
    assert result is not None
    assert result.source == _PYTHON_SRC
    assert result.file_path == str(f)
