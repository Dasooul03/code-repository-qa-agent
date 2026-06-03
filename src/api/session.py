"""GET /session/{id} — retrieve session history."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.db.session_store import get_session

router = APIRouter(prefix="/session", tags=["session"])


class MessageItem(BaseModel):
    """A single chat message."""

    role: str
    content: str


class SessionResponse(BaseModel):
    """Response body for session lookup."""

    session_id: str
    messages: list[MessageItem]


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session_history(session_id: str) -> SessionResponse:
    """Return the message history for a session."""
    entry = get_session(session_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    messages = [MessageItem(**m) for m in entry["messages"]]
    return SessionResponse(session_id=session_id, messages=messages)
