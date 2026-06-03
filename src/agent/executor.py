"""Executor node: runs one plan step per iteration."""

from typing import Any

from src.agent.state import AgentState
from src.agent.tools import (
    filesystem_tool,
    git_tool,
    retriever_tool,
    symbol_tool,
)
from src.retrieval.hybrid_retriever import HybridRetriever

MAX_ITERATIONS = 3


class Executor:
    """Executes one plan step per call, dispatching to the appropriate tool."""

    def __init__(
        self,
        retriever: HybridRetriever | None = None,
        repo_root: str = ".",
    ) -> None:
        self._retriever = retriever
        self._repo_root = repo_root

    async def __call__(self, state: AgentState) -> dict[str, Any]:
        """Execute the next plan step and return a partial state update."""
        iteration = state["iteration"]
        plan = state["plan"]

        if iteration >= MAX_ITERATIONS or iteration >= len(plan):
            return {}

        step = plan[iteration]
        tool_name: str = step["tool"]
        reason: str = step["reason"]

        if tool_name == "retriever" and self._retriever is not None:
            docs = await retriever_tool(reason, self._retriever)
            return {
                "retrieved_docs": state["retrieved_docs"] + docs,
                "tool_results": state["tool_results"]
                + [{"tool": "retriever", "query": reason, "count": len(docs)}],
                "iteration": iteration + 1,
            }

        if tool_name == "filesystem":
            result = filesystem_tool(reason, self._repo_root)
        elif tool_name == "git":
            result = git_tool(self._repo_root, target=reason)
        elif tool_name == "symbol":
            result = symbol_tool(reason, self._repo_root)
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return {
            "tool_results": state["tool_results"]
            + [{"tool": tool_name, "reason": reason, **result}],
            "iteration": iteration + 1,
        }
