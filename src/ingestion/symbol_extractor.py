"""Symbol extractor: pull function, class, method, and import symbols from AST."""

from dataclasses import dataclass

from tree_sitter import Node

from src.ingestion.chunker import (
    CLASS_NODE_TYPES,
    FUNCTION_NODE_TYPES,
    collect_nodes,
    get_node_name,
)
from src.ingestion.parser import ParseResult

_IMPORT_NODE_TYPES: dict[str, frozenset[str]] = {
    "python": frozenset(["import_statement", "import_from_statement"]),
    "java": frozenset(["import_declaration"]),
    "cpp": frozenset(["preproc_include"]),
    "javascript": frozenset(["import_statement"]),
    "typescript": frozenset(["import_statement"]),
    "tsx": frozenset(["import_statement"]),
}


@dataclass
class Symbol:
    """An extracted code symbol."""

    symbol: str
    type: str  # "function", "class", "method", or "import"
    file: str
    start: int
    end: int


def _import_name(node: Node, language: str) -> str:
    """Extract a display name from an import node."""
    if language == "python":
        for child in node.children:
            if child.type in ("dotted_name", "aliased_import", "relative_import"):
                if child.text is not None:
                    return child.text.decode("utf-8").split(" as ")[0].strip()
    elif language == "java":
        for child in node.children:
            if child.type == "scoped_identifier" and child.text is not None:
                return child.text.decode("utf-8")
    elif language == "cpp":
        for child in node.children:
            if child.type in ("string_literal", "system_lib_string"):
                if child.text is not None:
                    return child.text.decode("utf-8").strip('"<>')
    if node.text is not None:
        return node.text.decode("utf-8").split("\n")[0][:80]
    return "<import>"


def _has_class_ancestor(node: Node, class_types: frozenset[str]) -> bool:
    """Return True if any ancestor of node is a class-like node."""
    parent = node.parent
    while parent is not None:
        if parent.type in class_types:
            return True
        parent = parent.parent
    return False


def extract_symbols(result: ParseResult) -> list[Symbol]:
    """Extract all symbols from a parsed file."""
    language = result.language
    func_types = FUNCTION_NODE_TYPES.get(language, frozenset())
    class_types = CLASS_NODE_TYPES.get(language, frozenset())
    import_types = _IMPORT_NODE_TYPES.get(language, frozenset())
    all_types = func_types | class_types | import_types

    symbols: list[Symbol] = []
    for node in collect_nodes(result.tree.root_node, all_types):
        if node.type in import_types:
            sym_type = "import"
            name = _import_name(node, language)
        elif node.type in func_types:
            sym_type = (
                "method" if _has_class_ancestor(node, class_types) else "function"
            )
            name = get_node_name(node, language)
        else:
            sym_type = "class"
            name = get_node_name(node, language)

        symbols.append(
            Symbol(
                symbol=name,
                type=sym_type,
                file=result.file_path,
                start=node.start_point[0] + 1,
                end=node.end_point[0] + 1,
            )
        )

    return symbols
