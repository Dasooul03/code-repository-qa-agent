"""FastAPI application entry point."""

from fastapi import FastAPI

from src.api.health import router as health_router
from src.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    return app


app = create_app()
