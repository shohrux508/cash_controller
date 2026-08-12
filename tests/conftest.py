from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.container import create_app
from app.database.models import Base


@pytest.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create an in-memory SQLite engine for testing."""
    test_engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
    )
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create a session factory for testing."""
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
async def session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Yield a test database session."""
    async with session_factory() as sess:
        yield sess


@pytest.fixture
async def client(
    engine: AsyncEngine,
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient, None]:
    """Create an httpx AsyncClient wired to the test application."""
    app = create_app()
    # Manually initialize the container with test resources
    # instead of relying on lifespan (which uses real DB)
    import httpx as httpx_lib

    from app.core.container import AppContainer

    container = AppContainer()
    container.engine = engine
    container.session_factory = session_factory
    container.http_client = httpx_lib.AsyncClient(timeout=5.0)
    app.state.container = container

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await container.http_client.aclose()
