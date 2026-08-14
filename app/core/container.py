"""Application container: manages lifecycle of FastAPI, Telegram Bot, and Scheduler."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.api.v1 import health
from app.api.v1 import transactions
from app.core.config import settings
from app.database.engine import build_engine, build_session_factory
from app.database.models import Base
from app.logger import setup_logging


class AppContainer:
    """Manages the lifecycle of application-level resources."""

    __slots__ = ("engine", "session_factory")

    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]

    async def start(self) -> None:
        """Initialize database engine, create tables, and seed categories."""
        self.engine = build_engine(settings.database_url)
        self.session_factory = build_session_factory(self.engine)

        # Create tables if they don't exist (for SQLite without Alembic)
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Seed default categories
        from app.services.category_service import CategoryService

        async with self.session_factory() as session:
            await CategoryService.seed_default_categories(session)

        logger.info("Database initialized and categories seeded")

    async def stop(self) -> None:
        """Gracefully shut down all resources."""
        await self.engine.dispose()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup and shutdown."""
    setup_logging()

    # Initialize database
    container = AppContainer()
    await container.start()
    app.state.container = container

    # Start Telegram bot in background
    bot_task: asyncio.Task[None] | None = None
    if settings.bot_token:
        bot_task = asyncio.create_task(_run_bot(container.session_factory))
        logger.info("Telegram bot started in background")
    else:
        logger.warning("BOT_TOKEN not set — Telegram bot is disabled")

    yield

    # Shutdown
    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass

    from app.bot.scheduler import stop_scheduler

    stop_scheduler()
    await container.stop()
    logger.info("Application shutdown complete")


async def _run_bot(session_factory: async_sessionmaker[AsyncSession]) -> None:
    """Run the Telegram bot polling in background."""
    from aiogram import Bot, Dispatcher
    from aiogram.client.default import DefaultBotProperties

    from app.bot.handlers import main_router
    from app.bot.middlewares.auth import AuthMiddleware
    from app.bot.scheduler import start_scheduler

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    # Store session_factory in bot for handlers to access
    bot["session_factory"] = session_factory

    # Register middleware and handlers
    dp.message.middleware(AuthMiddleware())
    dp.include_router(main_router)

    # Start reminder scheduler
    start_scheduler(bot, session_factory)

    logger.info("Bot polling started")
    try:
        await dp.start_polling(bot, close_bot_session=True)
    except asyncio.CancelledError:
        logger.info("Bot polling stopped")
        await bot.session.close()


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
    app.include_router(transactions.router, prefix="/api/v1")
    return app
