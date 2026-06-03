"""Health-check endpoint."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health endpoint response body."""

    status: Literal["ok"]


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return service health status."""

    return HealthResponse(status="ok")
