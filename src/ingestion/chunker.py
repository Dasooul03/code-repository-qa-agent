"""AST-aware code chunker."""

from dataclasses import dataclass

from tree_sitter import Node

from src.ingestion.parser import ParseResult

# Function/method node types per language
FUNCTION_NODE_TYPES: dict[str, frozenset[str]] = {
    "python": frozenset(["function_definition"]),
    "java": frozenset(["method_declaration", "constructor_declaration"]),
    "cpp": frozenset(["function_definition"]),
    "javascript": frozenset(
        ["function_declaration", "method_definition", "function_expression"]
    ),
    "typescript": frozenset(
        ["function_declaration", "method_definition", "function_expression"]
    ),
    "tsx": frozenset(
        ["function_declaration", "method_definition", "function_expression"]
    ),
}

# Class/struct node types per language
CLASS_NODE_TYPES: dict[str, frozenset[str]] = {
    "python": frozenset(["class_definition"]),
    "java": frozenset(
        ["class_declaration", "interface_declaration", "enum_declaration"]
    ),
    "cpp": frozenset(["class_specifier", "struct_specifier"]),
    "javascript": frozenset(["class_declaration"]),
    "typescript": frozenset(["class_declaration"]),
    "tsx": frozenset(["class_declaration"]),
}


@dataclass
class Chunk:
    """A code chunk ready for embedding and indexing."""

    content: str
    symbol: str
    file_path: str
    start_line: int
    end_line: int
    chunk_type: str  # "function", "class", or "module"


def get_node_name(node: Node, language: str) -> str:
    """Extract the symbol name from a tree-sitter node."""
    name_node = node.child_by_field_name("name")
    if name_node is not None and name_node.text is not None:
        return name_node.text.decode("utf-8")
    # C++ function_definition wraps the name in nested declarators
    if language == "cpp":
        declarator = node.child_by_field_name("declarator")
        if declarator is not None:
            inner = declarator.child_by_field_name("declarator")
            if inner is not None and inner.text is not None:
                return inner.text.decode("utf-8")
            if declarator.text is not None:
                return declarator.text.decode("utf-8").split("(")[0].strip()
    return "<anonymous>"


def collect_nodes(root: Node, target_types: frozenset[str]) -> list[Node]:
    """Collect all nodes of the given types via DFS, always descending."""
    results: list[Node] = []
    stack: list[Node] = [root]
    while stack:
        node = stack.pop()
        if node.type in target_types:
            results.append(node)
        stack.extend(reversed(node.children))
    return results


def chunk_parse_result(result: ParseResult) -> list[Chunk]:
    """Chunk a parsed file into function, class, and module-level chunks."""
    language = result.language
    lines = result.source.splitlines()

    func_types = FUNCTION_NODE_TYPES.get(language, frozenset())
    class_types = CLASS_NODE_TYPES.get(language, frozenset())
    all_types = func_types | class_types

    chunks: list[Chunk] = []
    for node in collect_nodes(result.tree.root_node, all_types):
        chunk_type = "function" if node.type in func_types else "class"
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        content = "\n".join(lines[node.start_point[0] : node.end_point[0] + 1])
        chunks.append(
            Chunk(
                content=content,
                symbol=get_node_name(node, language),
                file_path=result.file_path,
                start_line=start_line,
                end_line=end_line,
                chunk_type=chunk_type,
            )
        )

    # Whole-file fallback when no functions or classes were found
    if not chunks:
        chunks.append(
            Chunk(
                content=result.source,
                symbol="<module>",
                file_path=result.file_path,
                start_line=1,
                end_line=len(lines) or 1,
                chunk_type="module",
            )
        )

    return chunks
