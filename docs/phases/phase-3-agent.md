# Phase 3: LangGraph Agent

**Commit:** `ad6c082 feat(phase-3): implement langgraph agent`
**Date:** 2026-06-03
**Agent:** Claude (claude-sonnet-4-6)
**Status:** COMPLETE

## Goal

Implement the full LangGraph agent pipeline with structured planning, multi-tool execution loop, and citation-aware answer synthesis.

## Files Created

| File | Purpose |
|------|---------|
| `src/agent/state.py` | `AgentState` TypedDict + `Plan`/`PlanStep` Pydantic models |
| `src/agent/planner.py` | Structured-output LLM planner → validated `Plan` |
| `src/agent/tools.py` | Four tool implementations: retriever/filesystem/git/symbol |
| `src/agent/executor.py` | Single-step tool dispatcher, `MAX_ITERATIONS=3` |
| `src/agent/synthesizer.py` | LLM answer generator with `file:start-end` citations |
| `src/agent/graph.py` | LangGraph StateGraph assembly with executor↔tool_node loop |
| `tests/agent/test_state.py` | PlanStep/Plan/AgentState/empty_state tests |
| `tests/agent/test_planner.py` | Planner tests with mocked LLM |
| `tests/agent/test_executor.py` | Executor tests: each tool + boundary conditions |
| `tests/agent/test_synthesizer.py` | Synthesizer + `_build_context` tests |
| `tests/agent/test_graph.py` | `_is_done` predicate + end-to-end graph integration test |

## Key Implementation Details

### Graph topology
```
query_analyzer → planner → executor ⟷ tool_node → synthesizer → END
                               ↑__________________|
```
`executor` and `tool_node` call the same `Executor` instance. Routing is controlled by `_is_done()`:
```python
def _is_done(state: AgentState) -> bool:
    return state["iteration"] >= MAX_ITERATIONS or state["iteration"] >= len(state["plan"])
```

### state.py — TypedDict + Pydantic dual schema
```python
class PlanStep(BaseModel):
    tool: str
    reason: str

class AgentState(TypedDict):
    query: str
    plan: list[dict[str, Any]]   # serialized as model_dump()
    retrieved_docs: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]
    answer: str
    iteration: int
```
TypedDict stores plan as dicts (not Pydantic objects) because LangGraph merges partial state dicts.

### planner.py — structured output
```python
self._chain = llm.with_structured_output(Plan)
# Handles both Plan object and dict responses from different LLM backends
result = await self._chain.ainvoke(messages)
if isinstance(result, dict):
    return Plan.model_validate(result)
return cast(Plan, result)
```

### executor.py — tool dispatch
```python
if tool_name == "retriever" and self._retriever is not None:
    docs = await retriever_tool(reason, self._retriever)
    return {"retrieved_docs": state["retrieved_docs"] + docs, ..., "iteration": iteration + 1}
# filesystem / git / symbol dispatch
```

### synthesizer.py — citation formatting
```python
def _build_context(state: AgentState) -> str:
    for doc in state["retrieved_docs"]:
        parts.append(f"# {path}:{start}-{end}\n{content}")
    for result in state["tool_results"]:
        if result.get("tool") != "retriever":
            parts.append(f"# Tool: {result.get('tool')}\n{result}")
```

## Bugs Fixed During Validation

| Error | Fix |
|-------|-----|
| `E501` line too long in graph.py docstring | Added `# noqa: E501` to the module docstring line |
| `F401` unused `Any` in planner.py | Removed (ruff --fix) |
| `F401` unused `patch`, `pytest` in tests | Removed (ruff --fix) |
| `dict` without type args (mypy strict) | Changed all `dict` / `list[dict]` → `dict[str, Any]` / `list[dict[str, Any]]` |
| `StateGraph` without type arg | Changed to `StateGraph[AgentState]` |
| `tests.*` mypy override not covering `tests.agent.*` | Added `"tests.*.*"` to override module list; also annotated helper functions directly |

## Commands Run

```
uv sync --all-groups
uv run black src/agent tests/agent  → 4 files reformatted
uv run ruff check --fix             → 9 auto-fixed, 1 manual (noqa)
uv run mypy src/agent tests/agent   → success
uv run pytest tests/agent -v        → 22/22 passed
uv run pytest -v                    → 59/59 passed (no regressions)
git commit ad6c082
```

## Validation

- black: ✓ | ruff: ✓ | mypy: ✓ | pytest: 59/59 ✓

## Next Phase

Phase 4 — MCP Tools
