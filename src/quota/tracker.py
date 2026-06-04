"""Thread-safe in-memory quota tracker with daily token limits and auto-reset.

Tracks token consumption across chat and embedding operations.
Supports both daily token quota and legacy per-call limits.
"""

import threading
import time
from dataclasses import dataclass, field

from src.config import get_settings

# Characters-per-token rough estimate (used for embedding text → token conversion).
# GPT-family tokenizers average ~4 characters per English token.
_CHARS_PER_TOKEN = 4


class QuotaExceededError(Exception):
    """Raised when an API usage quota has been exceeded."""

    def __init__(self, metric: str, used: int, limit: int) -> None:
        self.metric = metric
        self.used = used
        self.limit = limit
        super().__init__(
            f"Quota exceeded for '{metric}': {used} used, limit {limit}"
        )


def _today_key() -> str:
    """Return a date string (YYYY-MM-DD) used as the daily bucket key."""
    return time.strftime("%Y-%m-%d", time.localtime())


@dataclass
class QuotaTracker:
    """Thread-safe token / call tracker with daily reset for token quota."""

    _lock: threading.Lock = field(default_factory=threading.Lock)
    _today: str = field(default_factory=_today_key)

    # Daily token counters
    _tokens_used: int = 0  # total tokens consumed today

    # Legacy per-call counters (kept for backward compat)
    _chat_calls: int = 0
    _embedding_calls: int = 0

    # ── daily reset helper ───────────────────────────────────

    def _maybe_reset_daily(self) -> None:
        """Reset daily counters if the date has changed."""
        key = _today_key()
        if key != self._today:
            self._tokens_used = 0
            self._today = key

    # ── token-based checks ───────────────────────────────────

    def check_token_quota(self) -> None:
        """Raise QuotaExceededError if daily token limit is reached."""
        settings = get_settings()
        limit = (settings.usage_quota_daily_token_limit or 0)
        with self._lock:
            self._maybe_reset_daily()
            if limit > 0 and self._tokens_used >= limit:
                raise QuotaExceededError("daily_tokens", self._tokens_used, limit)

    def track_tokens(self, n: int) -> None:
        """Add *n* tokens to today's usage."""
        with self._lock:
            self._maybe_reset_daily()
            self._tokens_used += n

    # ── legacy call-based checks (keep backward compat) ───────

    def check_chat_quota(self) -> None:
        """Raise if chat call limit reached (legacy)."""
        settings = get_settings()
        max_chat = settings.usage_quota_max_chat_calls
        with self._lock:
            if max_chat is not None and max_chat > 0 and self._chat_calls >= max_chat:
                raise QuotaExceededError("chat_calls", self._chat_calls, max_chat)

    def check_embedding_quota(self) -> None:
        """Raise if embedding call limit reached (legacy)."""
        settings = get_settings()
        max_emb = settings.usage_quota_max_embedding_calls
        with self._lock:
            if (max_emb is not None and max_emb > 0
                    and self._embedding_calls >= max_emb):
                raise QuotaExceededError(
                    "embedding_calls", self._embedding_calls, max_emb
                )

    # ── trackers ─────────────────────────────────────────────

    def track_chat_call(self) -> None:
        """Increment chat call counter (legacy)."""
        with self._lock:
            self._chat_calls += 1

    def track_embedding_calls(self, n: int = 1) -> None:
        """Increment embedding call counter by n (legacy)."""
        with self._lock:
            self._embedding_calls += n

    # ── embedding text → token estimate ──────────────────────

    @staticmethod
    def estimate_text_tokens(text: str) -> int:
        """Rough token count: characters / CHARS_PER_TOKEN, min 1."""
        return max(1, len(text) // _CHARS_PER_TOKEN)

    @staticmethod
    def estimate_batch_tokens(texts: list[str]) -> int:
        """Sum token estimates for a batch of texts."""
        return sum(QuotaTracker.estimate_text_tokens(t) for t in texts)

    # ── status ───────────────────────────────────────────────

    def get_usage(self) -> dict:
        """Return current usage statistics as a dict."""
        settings = get_settings()
        with self._lock:
            self._maybe_reset_daily()
            limit = settings.usage_quota_daily_token_limit
            return {
                "daily_tokens": {
                    "used": self._tokens_used,
                    "limit": limit,
                    "date": self._today,
                },
                "chat_calls": {
                    "used": self._chat_calls,
                    "limit": settings.usage_quota_max_chat_calls,
                },
                "embedding_calls": {
                    "used": self._embedding_calls,
                    "limit": settings.usage_quota_max_embedding_calls,
                },
            }

    def reset(self) -> None:
        """Reset all counters to zero (for testing)."""
        with self._lock:
            self._tokens_used = 0
            self._chat_calls = 0
            self._embedding_calls = 0
            self._today = _today_key()


# Module-level singleton
_tracker: QuotaTracker | None = None
_tracker_lock = threading.Lock()


def get_quota_tracker() -> QuotaTracker:
    """Return the application-wide quota tracker singleton."""
    global _tracker
    if _tracker is None:
        with _tracker_lock:
            if _tracker is None:
                _tracker = QuotaTracker()
    return _tracker
