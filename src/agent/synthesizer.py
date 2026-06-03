"""Synthesizer node: generates the final answer with citations."""

from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from src.agent.state import AgentState

_SYSTEM = """\
You are a code assistant. Given a user query and retrieved context from a code \
repository, provide a precise, well-structured answer.

Rules:
- Cite every source as  file_path:start_line-end_line  (e.g. auth.py:10-40).
- Include short relevant code snippets where helpful.
- If context is insufficient, say so clearly.\
"""


class Synthesizer:
    """Generates a final answer from accumulated state using a chat LLM."""

    def __init__(self, llm: BaseChatModel) -> None:
        self._llm = llm

    async def __call__(self, state: AgentState) -> dict[str, Any]:
        """Return a partial state update with the generated answer."""
        context = _build_context(state)
        messages = [
            SystemMessage(content=_SYSTEM),
            HumanMessage(
                content=(
                    f"Query: {state['query']}\n\n" f"Context:\n{context}\n\n" "Answer:"
                )
            ),
        ]
        response = await self._llm.ainvoke(messages)
        return {"answer": str(response.content)}


def _build_context(state: AgentState) -> str:
    parts: list[str] = []
    for doc in state["retrieved_docs"]:
        path = doc.get("path", "unknown")
        start = doc.get("start_line", "?")
        end = doc.get("end_line", "?")
        content = doc.get("content", "")
        parts.append(f"# {path}:{start}-{end}\n{content}")
    for result in state["tool_results"]:
        if result.get("tool") != "retriever":
            parts.append(f"# Tool: {result.get('tool')}\n{result}")
    return "\n\n".join(parts) if parts else "No context retrieved."
