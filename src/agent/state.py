"""Agent state types and helpers."""

from typing import Any, TypedDict

from pydantic import BaseModel


class PlanStep(BaseModel):
    """A single step in the agent's execution plan."""

    tool: str
    reason: str


class Plan(BaseModel):
    """Structured execution plan output by the planner."""

    steps: list[PlanStep]


class AgentState(TypedDict):
    """Shared state flowing through all graph nodes."""

    query: str
    plan: list[dict[str, Any]]  # serialized PlanStep dicts: [{"tool": ..., "reason": ...}]
    retrieved_docs: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]
    answer: str
    iteration: int


def empty_state(query: str) -> AgentState:
    """Return an initialized AgentState for a given query."""
    return {
        "query": query,
        "plan": [],
        "retrieved_docs": [],
        "tool_results": [],
        "answer": "",
        "iteration": 0,
    }
