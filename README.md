# Code Repository Q&A Agent

Code Repository Q&A Agent is a phased project for building an agent system that can import code repositories, index source code, retrieve relevant context, call tools, and answer natural-language questions with file and line citations.

## Phase 0

This phase provides the runnable project scaffold:

- FastAPI application entry point
- `/health` endpoint
- Docker Compose services for API, Qdrant, PostgreSQL, and Redis
- Environment variable template
- Basic test, lint, type-check, and formatting configuration

## Local Development

Install dependencies:

```bash
uv sync --all-groups
```

Run the API:

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Check health:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Run validation:

```bash
uv run black src tests
uv run ruff check src tests
uv run mypy src tests
uv run pytest
```

Start all services when Docker is available:

```bash
docker compose up --build
```

## Project Skills

- `repoqa-project-lead`: primary phased implementation skill
- `repoqa-worklog-coordinator`: multi-agent log and handoff skill

Use `AGENT_WORKLOG.md` as the canonical coordination log.

