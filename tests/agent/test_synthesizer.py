"""Tests for the Synthesizer node."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

from src.agent.state import AgentState, empty_state
from src.agent.synthesizer import Synthesizer, _build_context


def _state_with_docs(
    docs: list[dict[str, Any]], tool_results: list[dict[str, Any]] | None = None
) -> AgentState:
    state = empty_state("test query")
    state["retrieved_docs"] = docs
    state["tool_results"] = tool_results or []
    return state


def test_build_context_with_docs() -> None:
    state = _state_with_docs(
        [
            {
                "path": "auth.py",
                "start_line": 1,
                "end_line": 10,
                "content": "def login():",
            }
        ]
    )
    ctx = _build_context(state)
    assert "auth.py:1-10" in ctx
    assert "def login():" in ctx


def test_build_context_empty() -> None:
    state = _state_with_docs([])
    ctx = _build_context(state)
    assert ctx == "No context retrieved."


def test_build_context_tool_results() -> None:
    state = _state_with_docs(
        [],
        tool_results=[{"tool": "filesystem", "path": "main.py", "content": "main()"}],
    )
    ctx = _build_context(state)
    assert "Tool: filesystem" in ctx


def test_build_context_retriever_results_excluded() -> None:
    state = _state_with_docs(
        [],
        tool_results=[{"tool": "retriever", "query": "auth", "count": 5}],
    )
    ctx = _build_context(state)
    assert ctx == "No context retrieved."


async def test_synthesizer_returns_answer() -> None:
    mock_response = MagicMock()
    mock_response.content = "The answer is 42."

    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)

    synth = Synthesizer(mock_llm)
    state = _state_with_docs(
        [{"path": "a.py", "start_line": 1, "end_line": 5, "content": "x = 1"}]
    )
    result = await synth(state)

    assert result["answer"] == "The answer is 42."
    mock_llm.ainvoke.assert_called_once()
