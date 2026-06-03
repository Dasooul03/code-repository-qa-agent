"""Tests for the Planner node."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from src.agent.planner import Planner
from src.agent.state import Plan, PlanStep


@pytest.fixture
def mock_llm() -> MagicMock:
    llm = MagicMock()
    chain = MagicMock()
    llm.with_structured_output.return_value = chain
    return llm


async def test_planner_returns_plan(mock_llm: MagicMock) -> None:
    plan = Plan(steps=[PlanStep(tool="retriever", reason="find auth")])
    mock_llm.with_structured_output.return_value.ainvoke = AsyncMock(return_value=plan)

    planner = Planner(mock_llm)
    result = await planner.aplan("how does auth work?")

    assert isinstance(result, Plan)
    assert result.steps[0].tool == "retriever"


async def test_planner_handles_dict_response(mock_llm: MagicMock) -> None:
    dict_plan = {"steps": [{"tool": "symbol", "reason": "find Executor"}]}
    mock_llm.with_structured_output.return_value.ainvoke = AsyncMock(
        return_value=dict_plan
    )

    planner = Planner(mock_llm)
    result = await planner.aplan("where is Executor defined?")

    assert isinstance(result, Plan)
    assert result.steps[0].tool == "symbol"


async def test_planner_uses_structured_output(mock_llm: MagicMock) -> None:
    plan = Plan(steps=[])
    mock_llm.with_structured_output.return_value.ainvoke = AsyncMock(return_value=plan)

    Planner(mock_llm)
    mock_llm.with_structured_output.assert_called_once_with(Plan)
