"""LangGraph agent graph: query_analyzer → planner → executor ↔ tool_node → synthesizer."""  # noqa: E501

from typing import Any

from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, StateGraph

from src.agent.executor import MAX_ITERATIONS, Executor
from src.agent.planner import Planner
from src.agent.state import AgentState, empty_state
from src.agent.synthesizer import Synthesizer
from src.retrieval.hybrid_retriever import HybridRetriever


def _is_done(state: AgentState) -> bool:
    return state["iteration"] >= MAX_ITERATIONS or state["iteration"] >= len(
        state["plan"]
    )


def build_graph(
    llm: BaseChatModel,
    retriever: HybridRetriever | None = None,
    repo_root: str = ".",
) -> Any:
    """Compile and return the LangGraph agent graph.

    Nodes:
        query_analyzer  normalises the query
        planner         produces a structured tool-call plan
        executor        runs plan step i (first call)
        tool_node       runs plan step i+1 (subsequent calls, loops with executor)
        synthesizer     generates the final answer
    """
    planner = Planner(llm)
    executor = Executor(retriever, repo_root)
    synthesizer = Synthesizer(llm)

    async def query_analyzer_node(state: AgentState) -> dict[str, Any]:
        return {"query": state["query"].strip()}

    async def planner_node(state: AgentState) -> dict[str, Any]:
        plan = await planner.aplan(state["query"])
        return {"plan": [s.model_dump() for s in plan.steps]}

    async def executor_node(state: AgentState) -> dict[str, Any]:
        return await executor(state)

    async def tool_node(state: AgentState) -> dict[str, Any]:
        return await executor(state)

    async def synthesizer_node(state: AgentState) -> dict[str, Any]:
        return await synthesizer(state)

    graph: StateGraph[AgentState] = StateGraph(AgentState)
    graph.add_node("query_analyzer", query_analyzer_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("tool_node", tool_node)
    graph.add_node("synthesizer", synthesizer_node)

    graph.set_entry_point("query_analyzer")
    graph.add_edge("query_analyzer", "planner")
    graph.add_edge("planner", "executor")

    # executor → tool_node (more iterations) or synthesizer (done)
    graph.add_conditional_edges(
        "executor",
        lambda s: "synthesizer" if _is_done(s) else "tool_node",
    )
    # tool_node → executor (more iterations) or synthesizer (done)
    graph.add_conditional_edges(
        "tool_node",
        lambda s: "synthesizer" if _is_done(s) else "executor",
    )
    graph.add_edge("synthesizer", END)

    return graph.compile()


async def run_agent(
    query: str,
    llm: BaseChatModel,
    retriever: HybridRetriever | None = None,
    repo_root: str = ".",
) -> str:
    """Run the agent end-to-end and return the final answer string."""
    compiled = build_graph(llm, retriever, repo_root)
    result: AgentState = await compiled.ainvoke(empty_state(query))
    return result["answer"]
