---
name: repoqa-project-lead
description: Act as the primary project-lead skill for building the Code Repository Q&A Agent. Use when the user asks to implement, continue, coordinate, or review the main repository Q&A project across phases, including GitHub import, AST-aware chunking, hybrid retrieval, LangGraph agent reasoning, MCP tools, FastAPI streaming, session memory, and React UI. Enforce phased execution, teaching-mode reporting, validation, Git discipline, and work-log handoff with other agents.
---

# RepoQA Project Lead

## Mission

Build an agent system that understands code repositories and answers natural-language questions about them.

The completed system must support:

- GitHub repository import
- AST-aware code chunking
- Hybrid retrieval
- LangGraph agent reasoning
- MCP tool calls
- Streaming Q&A
- Session memory
- React web UI

Typical questions the system must eventually answer:

- Where is the project entry point?
- What is the user login flow?
- Where is Redis used?
- How does `OrderService` work?
- Which functions call `login()`?
- What are the system dependencies?

## Required Architecture

Implement toward this architecture:

```text
User
  -> FastAPI Gateway
  -> LangGraph Agent
       -> Retriever
       -> MCP Filesystem
       -> MCP Git
       -> MCP Symbol
       -> MCP Dependencies
  -> LLM
  -> Answer
```

Implement the data pipeline:

```text
Repository
  -> Parser
  -> Chunker
  -> Embedding
  -> Qdrant
```

## Non-Negotiable Rules

Prioritize core capability before production extras.

Do not implement these before the core phases are complete:

- Kubernetes
- Helm
- Prometheus
- Grafana
- JWT
- ACL
- Multi-tenancy
- DevOps enhancements

Implement these first:

- Repository indexing
- Vector retrieval
- Agent reasoning
- MCP tools
- API service

Complete exactly one phase at a time. Do not develop multiple phases in parallel. After each phase, pause and wait for user confirmation before continuing.

All committed code must be runnable. Do not leave pseudocode, TODO placeholders, or mock implementations. Code must pass:

- `ruff`
- `mypy`
- `pytest`

Favor the simplest working implementation first. Optimize performance after the system works. Add production hardening only after the core system is complete.

## Multi-Agent Coordination

Treat this skill as the main project controller. When other agents contribute work, require a handoff summary before integrating or continuing their work.

Maintain the canonical project log at `AGENT_WORKLOG.md` in the repository root. After every meaningful step, update or request an update to the log with:

- Current phase and step
- Agent or role that performed the work
- Files changed
- Commands run and results
- Decisions made
- Open issues or blockers
- Next recommended action

If a separate log-coordination agent is available, use `repoqa-worklog-coordinator` to normalize handoffs, merge logs, and produce the current project status before starting a new phase or assigning work to another agent.

Before continuing work from another agent, read `AGENT_WORKLOG.md` and verify the claimed state against the repository when practical.

## Teaching Mode

After every completed step or phase, pause and explain:

- What problem this step solved
- Why this design was chosen
- Which technologies are involved
- Which files changed
- The core code logic
- What the next step will be

Use this output format after each completed step:

```markdown
**当前阶段**
Phase X

**本次完成内容**
Detailed description

**修改文件**
- file1.py
- file2.py

**技术讲解**
Implementation principles

**为什么这样设计**
Design rationale

**下一步计划**
Next step

**等待确认**
等待用户继续
```

Do not continue to the next phase until the user explicitly confirms.

## Technology Stack

Use this stack unless the existing repository strongly requires a compatible adjustment:

- Backend: Python 3.12, FastAPI, LangGraph, LangChain, Pydantic v2
- Storage: Qdrant, PostgreSQL, Redis
- Parser: tree-sitter
- Embedding: `text-embedding-3-large`
- LLM: Claude Sonnet or GPT-4.1
- Frontend: React, shadcn/ui

## Target Project Structure

Create or evolve the repository toward this structure:

```text
src/
  agent/
    state.py
    graph.py
    planner.py
    executor.py
    synthesizer.py
    tools.py
  ingestion/
    parser.py
    chunker.py
    symbol_extractor.py
    indexer.py
  retrieval/
    hybrid_retriever.py
    reranker.py
    qdrant_store.py
  mcp/
    filesystem/
    git/
    symbol/
    deps/
  api/
    chat.py
    repository.py
    health.py
  db/
    postgres.py
    redis.py
  config.py
  main.py
```

## Phase 0: Project Scaffold

Goal: create a runnable project scaffold.

Create:

- `pyproject.toml`
- `docker-compose.yml`
- `.env.example`
- `Makefile`
- `README.md`
- `src/main.py`
- `src/api/health.py`

Docker services must start:

- Qdrant
- PostgreSQL
- Redis
- FastAPI

Acceptance criteria:

- `docker compose up` starts all services successfully.
- `GET /health` returns:

```json
{"status":"ok"}
```

Pause after completion and wait for user confirmation.

## Phase 1: Code Indexing

Goal: implement the code indexing system.

Step 1: implement `src/ingestion/parser.py`.

- Use `tree-sitter`.
- Support Python, Java, C++, JavaScript, and TypeScript.
- Output AST-aware parse results.

Step 2: implement `src/ingestion/chunker.py`.

- Chunk by Function, then Class, then Module.
- Preserve docstring, path, start line, and end line.
- Output records shaped like:

```json
{"content":"...","symbol":"login","file_path":"auth.py","start_line":10,"end_line":40}
```

Step 3: implement `src/ingestion/symbol_extractor.py`.

- Extract Function, Class, Method, and Import symbols.
- Output records shaped like:

```json
{"symbol":"login","type":"function","file":"auth.py","start":10,"end":40}
```

Step 4: implement `src/ingestion/indexer.py`.

- Pipeline: Repository -> Parse -> Chunk -> Embedding -> Qdrant.
- Support SHA256-based incremental updates.

Acceptance criteria:

- A 50K-line Python project can be indexed in under 5 minutes.

Pause after completion and wait for user confirmation.

## Phase 2: Retrieval

Goal: implement hybrid retrieval.

Implement `src/retrieval/hybrid_retriever.py`.

Required flow:

```text
Query
  -> Dense Search
  -> BM25 Search
  -> RRF Fusion
  -> CrossEncoder ReRank
  -> TopK
```

Return records shaped like:

```json
[{"content":"...","score":0.95,"path":"..."}]
```

Acceptance criteria:

- `MRR@5 > 0.7` on the project evaluation set.

Pause after completion and wait for user confirmation.

## Phase 3: LangGraph Agent

Goal: implement the LangGraph agent.

Implement `src/agent/state.py` with `AgentState` fields:

- `query`
- `plan`
- `retrieved_docs`
- `tool_results`
- `answer`
- `iteration`

Implement `src/agent/graph.py` with this flow:

```text
query_analyzer
  -> planner
  -> executor
  -> tool_node
  -> synthesizer
```

Allow `executor <-> tool_node` loops with a maximum of 3 iterations.

Implement `src/agent/planner.py`.

- Output JSON shaped like:

```json
{"steps":[{"tool":"retriever","reason":"查找OrderService"}]}
```

- Validate planner output with JSON Schema or Pydantic.

Implement `src/agent/executor.py`.

Support these tools:

- `retriever`
- `filesystem`
- `git`
- `symbol`

Implement `src/agent/synthesizer.py`.

- Generate final answers with file paths, line numbers, and relevant code snippets.

Acceptance criteria:

- The agent can answer: `用户登录流程是什么？`

Pause after completion and wait for user confirmation.

## Phase 4: MCP Tools

Goal: implement MCP-backed tools and adapt them into LangChain tools.

Implement Filesystem MCP:

- `read_file`
- `list_dir`
- `search_file`

Implement Git MCP:

- `git_log`
- `git_blame`
- `git_diff`

Implement Symbol MCP:

- `find_symbol`
- `find_references`
- `find_definition`

Implement Dependency MCP:

- `dependency_graph`
- `package_info`

Implement `MCPToolAdapter`.

- Convert MCP tools into LangChain `StructuredTool` instances automatically.

Acceptance criteria:

- The agent successfully calls MCP tools during question answering.

Pause after completion and wait for user confirmation.

## Phase 5: API

Goal: implement FastAPI endpoints.

Implement:

- `POST /chat`
- `POST /repo/register`
- `GET /session/{id}`
- `GET /health`

Chat must support SSE streaming and return final answers shaped like:

```json
{"answer":"..."}
```

Acceptance criteria:

- A browser can receive token streams in real time.

Pause after completion and wait for user confirmation.

## Phase 6: Web UI

Goal: implement a complete React UI.

Implement:

- Chat window
- Code citations
- Repository management
- Session history
- Clickable code references

Use citation format:

```text
auth.py:10-40
```

Acceptance criteria:

- A user can complete the full repository Q&A flow from the web UI.

Pause after completion and wait for user confirmation.

## Code Standards

Follow these standards throughout:

- Add type annotations to every function.
- Add docstrings to every public function.
- Use Pydantic v2.
- Use `async` / `await` for I/O-oriented paths.
- Put configuration in `src/config.py`.
- Never hard-code API keys.
- Maintain test coverage of at least 80%.
- Pass Ruff.
- Pass MyPy.
- Format with Black.

## Git Standards

Commit once per completed phase.

Use commit messages shaped like:

```text
feat(phase-x): description
```

Examples:

```text
feat(phase-1): implement repository indexing pipeline
feat(phase-2): implement hybrid retrieval
feat(phase-3): implement langgraph agent
```

## Completion Standard

The project is complete only when it has:

- GitHub repository import
- AST-aware chunking
- Hybrid retrieval
- LangGraph agent
- MCP tool calls
- FastAPI endpoints
- Streaming Q&A
- Session memory
- React frontend
