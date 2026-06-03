# Project Start Checklist

Use this checklist before starting Phase 0 of the Code Repository Q&A Agent project.

## 1. Skill Setup

- Confirm `repoqa-project-lead` is the primary project execution skill.
- Confirm `repoqa-worklog-coordinator` is the worklog and handoff skill.
- Decide whether to install both skills into the Codex skill directory for automatic discovery.
- Keep `AGENT_WORKLOG.md` as the canonical coordination log.

## 2. Runtime Decisions

Confirm these choices before implementation begins:

- Python package manager: `uv`, Poetry, or plain `pip`
- Python version target: Python 3.12
- Frontend package manager: `pnpm`, npm, or yarn
- Backend app module path: `src/main.py`
- Docker Compose command: `docker compose`
- Local API port: `8000`
- Local frontend port: `3000` or `5173`

Recommended defaults:

- Python package manager: `uv`
- Frontend package manager: `pnpm`
- Backend port: `8000`
- Frontend port: `5173`

## 3. Secret And Model Configuration

Create `.env.example` during Phase 0 with placeholders for:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `QDRANT_URL`
- `POSTGRES_DSN`
- `REDIS_URL`
- `EMBEDDING_MODEL`
- `CHAT_MODEL`

Never commit real API keys.

## 4. Agent Roles

Suggested multi-agent roles:

- `repoqa-project-lead`: Owns phase planning, implementation order, acceptance checks, and user-facing teaching summaries.
- `repoqa-worklog-coordinator`: Owns `AGENT_WORKLOG.md`, handoff normalization, status summaries, and conflict detection.
- Backend agent: Implements FastAPI, config, persistence, tests, and service wiring.
- Ingestion agent: Implements parser, chunker, symbol extraction, indexing, and related tests.
- Retrieval agent: Implements dense search, BM25, RRF, reranking, Qdrant integration, and retrieval evaluation.
- Agent-runtime agent: Implements LangGraph state, planner, executor, tool loop, and synthesizer.
- MCP agent: Implements filesystem, git, symbol, dependency tools, and LangChain tool adapter.
- Frontend agent: Implements React UI, repository management, chat streaming, citations, and session history.

Only one phase should be active at a time even if multiple agents help within that phase.

## 5. Handoff Rule

Every agent must provide a handoff entry before stopping work.

Required handoff fields:

- Agent or role
- Phase and step
- Files changed
- Commands run
- Validation result
- Decisions made
- Blockers
- Next recommended action

The log coordinator should merge the handoff into `AGENT_WORKLOG.md`.

## 6. Acceptance Baseline

Before leaving each phase, run the strongest practical validation available:

- Format: `black`
- Lint: `ruff`
- Types: `mypy`
- Tests: `pytest`
- Runtime smoke test for the phase

If a command cannot run, record why in `AGENT_WORKLOG.md`.

## 7. Phase 0 Readiness

Start Phase 0 only after these are clear:

- Package manager selected
- Docker is available
- Backend port selected
- `.env.example` shape agreed
- User confirms the project should begin

