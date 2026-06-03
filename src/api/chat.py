"""POST /chat — SSE streaming chat endpoint."""

import asyncio
import json
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from src.agent.graph import run_agent
from src.config import Settings, get_settings
from src.db.session_store import append_message, create_session, get_session

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""

    query: str = Field(min_length=1, max_length=4096)
    session_id: str | None = Field(default=None)
    repo_root: str = Field(default=".")


class ChatResponse(BaseModel):
    """Non-streaming response body (used when streaming is not requested)."""

    answer: str
    session_id: str


def _make_llm(settings: Settings) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.chat_model,
        api_key=settings.openai_api_key,  # type: ignore[arg-type]
        streaming=True,
    )


async def _token_stream(
    query: str,
    repo_root: str,
    session_id: str,
    settings: Settings,
) -> AsyncGenerator[str, None]:
    """Run the agent and yield SSE-formatted chunks."""
    llm = _make_llm(settings)
    try:
        answer = await run_agent(query, llm, repo_root=repo_root)
    except Exception as exc:  # noqa: BLE001
        yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        return

    append_message(session_id, "user", query)
    append_message(session_id, "assistant", answer)

    # Emit the full answer in one chunk (agent is non-streaming internally)
    # then send the done sentinel
    chunk_size = 80
    for i in range(0, len(answer), chunk_size):
        chunk = answer[i : i + chunk_size]
        yield f"data: {json.dumps({'delta': chunk})}\n\n"
        await asyncio.sleep(0)  # yield control to event loop

    yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"


@router.post("")
async def chat(
    body: ChatRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> StreamingResponse:
    """Run the agent on a query and stream the answer as SSE."""
    session_id = body.session_id or create_session()
    if body.session_id and get_session(body.session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    return StreamingResponse(
        _token_stream(body.query, body.repo_root, session_id, settings),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
