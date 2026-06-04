"""GET /quota — API usage quota status."""

from fastapi import APIRouter
from pydantic import BaseModel

from src.quota import get_quota_tracker

router = APIRouter(prefix="/quota", tags=["quota"])


class UsageMetric(BaseModel):
    """Usage for a single metric."""

    used: int
    limit: int | None


class DailyTokenMetric(BaseModel):
    """Daily token usage."""

    used: int
    limit: int | None
    date: str


class QuotaResponse(BaseModel):
    """Current usage quota status."""

    daily_tokens: DailyTokenMetric
    chat_calls: UsageMetric
    embedding_calls: UsageMetric


@router.get("", response_model=QuotaResponse)
async def get_quota() -> QuotaResponse:
    """Return current API usage quota status."""
    usage = get_quota_tracker().get_usage()
    return QuotaResponse(
        daily_tokens=DailyTokenMetric(**usage["daily_tokens"]),
        chat_calls=UsageMetric(**usage["chat_calls"]),
        embedding_calls=UsageMetric(**usage["embedding_calls"]),
    )
