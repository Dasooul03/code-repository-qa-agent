"""AST-aware code parser using tree-sitter."""

from dataclasses import dataclass
from pathlib import Path

import tree_sitter_cpp as tscpp
import tree_sitter_java as tsjava
import tree_sitter_javascript as tsjavascript
import tree_sitter_python as tspython
import tree_sitter_typescript as tstypescript
from tree_sitter import Language, Parser, Tree

EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".java": "java",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "cpp",
    ".h": "cpp",
    ".hpp": "cpp",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
}

_LANGUAGES: dict[str, Language] = {
    "python": Language(tspython.language()),
    "java": Language(tsjava.language()),
    "cpp": Language(tscpp.language()),
    "javascript": Language(tsjavascript.language()),
    "typescript": Language(tstypescript.language_typescript()),
    "tsx": Language(tstypescript.language_tsx()),
}

_PARSERS: dict[str, Parser] = {name: Parser(lang) for name, lang in _LANGUAGES.items()}


@dataclass
class ParseResult:
    """Result of parsing a single source file."""

    file_path: str
    language: str
    source: str
    tree: Tree


def parse_file(path: Path) -> ParseResult | None:
    """Parse a source file and return an AST parse result.

    Returns None if the file extension is not supported.
    """
    ext = path.suffix.lower()
    language = EXTENSION_TO_LANGUAGE.get(ext)
    if language is None:
        return None

    parser = _PARSERS[language]
    source = path.read_text(encoding="utf-8", errors="replace")
    tree = parser.parse(bytes(source, "utf-8"))

    return ParseResult(
        file_path=str(path),
        language=language,
        source=source,
        tree=tree,
    )


def get_supported_extensions() -> frozenset[str]:
    """Return the set of file extensions supported by the parser."""
    return frozenset(EXTENSION_TO_LANGUAGE.keys())
