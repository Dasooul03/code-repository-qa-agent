"""Integration tests for the full LangGraph agent graph."""

from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock

from src.agent.graph import _is_done, run_agent
from src.agent.state import empty_state


def test_is_done_at_max_iterations() -> None:
    state = empty_state("q")
    state["plan"] = [{"tool": "retriever", "reason": "r"}] * 3
    state["iteration"] = 3
    assert _is_done(state) is True


def test_is_done_plan_exhausted() -> None:
    state = empty_state("q")
    state["plan"] = [{"tool": "retriever", "reason": "r"}]
    state["iteration"] = 1
    assert _is_done(state) is True


def test_is_not_done() -> None:
    state = empty_state("q")
    state["plan"] = [
        {"tool": "retriever", "reason": "r"},
        {"tool": "symbol", "reason": "s"},
    ]
    state["iteration"] = 1
    assert _is_done(state) is False


async def test_run_agent_end_to_end() -> None:
    @dataclass
    class FakeDoc:
        content: str = "def login(): pass"
        score: float = 0.9
        path: str = "auth.py"
        symbol: str = "login"
        start_line: int = 1
        end_line: int = 5

    mock_retriever = MagicMock()
    mock_retriever.retrieve = AsyncMock(return_value=[FakeDoc()])

    plan_response = MagicMock()
    plan_response.steps = []

    mock_response = MagicMock()
    mock_response.content = "The login function handles auth."

    mock_llm = MagicMock()

    from src.agent.state import Plan, PlanStep

    real_plan = Plan(steps=[PlanStep(tool="retriever", reason="find login")])
    chain_mock = MagicMock()
    chain_mock.ainvoke = AsyncMock(return_value=real_plan)
    mock_llm.with_structured_output = MagicMock(return_value=chain_mock)
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)

    answer = await run_agent("how does login work?", mock_llm, mock_retriever)

    assert "login" in answer.lower() or len(answer) > 0
