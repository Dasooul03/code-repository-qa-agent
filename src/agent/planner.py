"""Plan-generation node: calls LLM to produce a structured execution plan."""

from typing import cast

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from src.agent.state import Plan

_SYSTEM = """\
You are a code repository analyst. Given a user query about a codebase, create a \
minimal retrieval plan using the tools below.

Available tools:
- retriever  : semantic/keyword search over indexed code chunks
- filesystem : read a specific file by path
- git        : query git history (log, blame, diff)
- symbol     : look up where a function/class/symbol is defined

Respond with a JSON plan: {"steps": [{"tool": "...", "reason": "..."}]}
Use at most 3 steps. Prefer retriever first.\
"""


class Planner:
    """Generates a structured plan from a query using a structured-output LLM."""

    def __init__(self, llm: BaseChatModel) -> None:
        self._chain = llm.with_structured_output(Plan)

    async def aplan(self, query: str) -> Plan:
        """Produce a Plan for the given query."""
        messages = [
            SystemMessage(content=_SYSTEM),
            HumanMessage(content=f"Query: {query}"),
        ]
        result = await self._chain.ainvoke(messages)
        if isinstance(result, dict):
            return Plan.model_validate(result)
        return cast(Plan, result)
