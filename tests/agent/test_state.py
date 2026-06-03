"""Tests for agent state types and helpers."""

from src.agent.state import AgentState, Plan, PlanStep, empty_state


def test_plan_step_valid() -> None:
    step = PlanStep(tool="retriever", reason="find auth logic")
    assert step.tool == "retriever"
    assert step.reason == "find auth logic"


def test_plan_valid() -> None:
    plan = Plan(steps=[PlanStep(tool="retriever", reason="q")])
    assert len(plan.steps) == 1


def test_empty_state_fields() -> None:
    state: AgentState = empty_state("how does auth work?")
    assert state["query"] == "how does auth work?"
    assert state["plan"] == []
    assert state["retrieved_docs"] == []
    assert state["tool_results"] == []
    assert state["answer"] == ""
    assert state["iteration"] == 0


def test_plan_step_model_dump() -> None:
    step = PlanStep(tool="symbol", reason="find Executor")
    dumped = step.model_dump()
    assert dumped == {"tool": "symbol", "reason": "find Executor"}
