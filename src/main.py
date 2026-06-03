"""FastAPI application entry point."""

from fastapi import FastAPI

from src.api.chat import router as chat_router
from src.api.health import router as health_router
from src.api.repository import router as repo_router
from src.api.session import router as session_router
from src.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(repo_router)
    app.include_router(session_router)
    return app


app = create_app()
