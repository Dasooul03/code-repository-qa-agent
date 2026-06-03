.PHONY: install format lint typecheck test check run docker-up

install:
	uv sync --all-groups

format:
	uv run black src tests

lint:
	uv run ruff check src tests

typecheck:
	uv run mypy src tests

test:
	uv run pytest

check: format lint typecheck test

run:
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

docker-up:
	docker compose up --build

