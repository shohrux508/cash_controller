"""APScheduler integration for sending reminders at scheduled times."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

if TYPE_CHECKING:
    from aiogram import Bot
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.services.reminder_service import ReminderService

_scheduler: AsyncIOScheduler | None = None


async def _check_reminders(bot: Bot, session_factory: async_sessionmaker[AsyncSession]) -> None:
    """Check and send reminders that match the current hour:minute."""
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute

    async with session_factory() as session:
        reminders = await ReminderService.get_all_active_reminders(session)

    for reminder in reminders:
        if reminder.hour == current_hour and reminder.minute == current_minute:
            try:
                await bot.send_message(
                    chat_id=reminder.user.telegram_id,
                    text=(
                        f"⏰ <b>Напоминание!</b>\n\n"
                        f"{reminder.message}"
                    ),
                )
            except Exception as e:
                logger.error(f"Failed to send reminder to user {reminder.user_id}: {e}")


def start_scheduler(
    bot: Bot, session_factory: async_sessionmaker[AsyncSession]
) -> AsyncIOScheduler:
    """Start the APScheduler with reminder checking job."""
    global _scheduler
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        _check_reminders,
        "cron",
        minute="*",
        args=[bot, session_factory],
        id="check_reminders",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Scheduler started — checking reminders every minute")
    return _scheduler


def stop_scheduler() -> None:
    """Stop the scheduler gracefully."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
        _scheduler = None
