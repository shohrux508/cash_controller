from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.api.v1 import health
from app.core.config import settings
from app.database.engine import build_engine, build_session_factory
from app.logger import setup_logging


class AppContainer:
    """Manages the lifecycle of application-level resources."""

    __slots__ = ("engine", "session_factory", "http_client")

    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    http_client: httpx.AsyncClient

    async def start(self) -> None:
        """Initialize all resources."""
        self.engine = build_engine(settings.database_url)
        self.session_factory = build_session_factory(self.engine)
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def stop(self) -> None:
        """Gracefully shut down all resources."""
        await self.http_client.aclose()
        await self.engine.dispose()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup and shutdown."""
    setup_logging()
    container = AppContainer()
    await container.start()
    app.state.container = container
    yield
    await container.stop()


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router, prefix="/api/v1")
    return app
