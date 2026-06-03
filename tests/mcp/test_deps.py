"""Tests for dependency MCP tools."""

from pathlib import Path

from src.mcp.deps.tools import dependency_graph, package_info


def test_dependency_graph_collects_imports(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("import os\nfrom pathlib import Path\n")
    result = dependency_graph(str(tmp_path))
    assert "main.py" in result["graph"]
    assert "os" in result["graph"]["main.py"]
    assert "pathlib" in result["graph"]["main.py"]


def test_dependency_graph_deduplicates(tmp_path: Path) -> None:
    (tmp_path / "dup.py").write_text("import os\nimport os\n")
    result = dependency_graph(str(tmp_path))
    assert result["graph"]["dup.py"].count("os") == 1


def test_package_info_reads_pyproject(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "myapp"\nversion = "0.1.0"\n'
        'dependencies = [\n    "fastapi>=0.115.0",\n    "pydantic>=2.0",\n]\n'
    )
    result = package_info(str(tmp_path))
    assert result["source"] == "pyproject.toml"
    assert result["name"] == "myapp"
    assert result["version"] == "0.1.0"
    assert any("fastapi" in d for d in result["dependencies"])


def test_package_info_reads_requirements(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("fastapi==0.115.0\npydantic>=2.0\n")
    result = package_info(str(tmp_path))
    assert result["source"] == "requirements.txt"
    assert "fastapi==0.115.0" in result["dependencies"]


def test_package_info_missing_returns_error(tmp_path: Path) -> None:
    result = package_info(str(tmp_path))
    assert "error" in result
