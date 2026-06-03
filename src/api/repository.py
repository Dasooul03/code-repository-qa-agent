"""POST /repo/register — register a repository for indexing."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

from src.config import Settings, get_settings
from src.ingestion.indexer import index_repository

router = APIRouter(prefix="/repo", tags=["repository"])

# Track in-progress indexing jobs: repo_path → status
_jobs: dict[str, str] = {}


class RegisterRequest(BaseModel):
    """Request body for repo registration."""

    repo_path: str = Field(description="Absolute path to the repository root")


class RegisterResponse(BaseModel):
    """Response body after repo registration."""

    repo_path: str
    status: str


async def _run_indexing(repo_path: str, settings: Settings) -> None:
    """Background task: index repo and update job status."""


    _jobs[repo_path] = "indexing"
    try:
        await index_repository(repo_path)
        _jobs[repo_path] = "ready"
    except Exception as exc:  # noqa: BLE001
        _jobs[repo_path] = f"error: {exc}"


@router.post("/register", response_model=RegisterResponse)
async def register_repository(
    body: RegisterRequest,
    background_tasks: BackgroundTasks,
    settings: Annotated[Settings, Depends(get_settings)],
) -> RegisterResponse:
    """Register a repository and start background indexing."""
    repo_path = body.repo_path
    if not Path(repo_path).is_dir():
        raise HTTPException(status_code=400, detail=f"Path not found: {repo_path}")

    if _jobs.get(repo_path) == "indexing":
        return RegisterResponse(repo_path=repo_path, status="indexing")

    background_tasks.add_task(_run_indexing, repo_path, settings)
    _jobs[repo_path] = "queued"
    return RegisterResponse(repo_path=repo_path, status="queued")


@router.get("/status/{repo_path:path}", response_model=RegisterResponse)
async def indexing_status(repo_path: str) -> RegisterResponse:
    """Return the current indexing status for a repository."""
    status = _jobs.get(repo_path)
    if status is None:
        raise HTTPException(status_code=404, detail="Repository not registered")
    return RegisterResponse(repo_path=repo_path, status=status)
