from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from fastapi import Request

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session from the application container."""
    from app.core.container import AppContainer

    container: AppContainer = request.app.state.container
    async with container.session_factory() as session:
        yield session
