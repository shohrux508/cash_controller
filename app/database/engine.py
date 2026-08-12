from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def build_engine(url: str) -> AsyncEngine:
    """Create an async SQLAlchemy engine."""
    connect_args: dict[str, bool] = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_async_engine(url, echo=False, connect_args=connect_args)


def build_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory bound to the given engine."""
    return async_sessionmaker(engine, expire_on_commit=False)
