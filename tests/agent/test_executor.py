"""Tests for the Executor node."""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from src.agent.executor import MAX_ITERATIONS, Executor
from src.agent.state import AgentState, empty_state


def _state_with_plan(tools: list[str], iteration: int = 0) -> AgentState:
    state = empty_state("test query")
    state["plan"] = [{"tool": t, "reason": f"reason for {t}"} for t in tools]
    state["iteration"] = iteration
    return state


async def test_executor_retriever_tool() -> None:
    @dataclass
    class FakeResult:
        content: str = "code"
        score: float = 0.9
        path: str = "foo.py"
        symbol: str = "foo"
        start_line: int = 1
        end_line: int = 10

    mock_retriever = MagicMock()
    mock_retriever.retrieve = AsyncMock(return_value=[FakeResult()])

    executor = Executor(retriever=mock_retriever)
    state = _state_with_plan(["retriever"])
    result = await executor(state)

    assert "retrieved_docs" in result
    assert result["iteration"] == 1
    assert len(result["retrieved_docs"]) == 1


async def test_executor_filesystem_tool(tmp_path: Path) -> None:
    test_file = tmp_path / "hello.py"
    test_file.write_text("print('hello')")

    executor = Executor(repo_root=str(tmp_path))
    state = _state_with_plan(["filesystem"])
    state["plan"][0]["reason"] = "hello.py"
    result = await executor(state)

    assert result["iteration"] == 1
    assert any(r.get("tool") == "filesystem" for r in result["tool_results"])


async def test_executor_symbol_tool(tmp_path: Path) -> None:
    (tmp_path / "foo.py").write_text("class Executor:\n    pass\n")

    executor = Executor(repo_root=str(tmp_path))
    state = _state_with_plan(["symbol"])
    state["plan"][0]["reason"] = "Executor"
    result = await executor(state)

    assert result["iteration"] == 1
    assert any(r.get("tool") == "symbol" for r in result["tool_results"])


async def test_executor_unknown_tool() -> None:
    executor = Executor()
    state = _state_with_plan(["unknown_tool"])
    result = await executor(state)

    assert result["iteration"] == 1
    assert "error" in result["tool_results"][0]


async def test_executor_stops_at_max_iterations() -> None:
    executor = Executor()
    state = _state_with_plan(["retriever"], iteration=MAX_ITERATIONS)
    result = await executor(state)

    assert result == {}


async def test_executor_stops_when_plan_exhausted() -> None:
    executor = Executor()
    state = _state_with_plan(["retriever"], iteration=1)
    # plan has 1 step, iteration is already 1 → exhausted
    result = await executor(state)

    assert result == {}
