from __future__ import annotations

from datetime import datetime
from typing import Any

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.utils import format_amount, format_date_short
from app.services.transaction_service import TransactionService

router = Router()


def _build_summary_text(title: str, summary: dict[str, Any]) -> str:
    """Format a period summary into a readable message."""
    income: int = summary.get("income", 0)
    expense: int = summary.get("expense", 0)
    balance: int = summary.get("balance", 0)
    by_category: list[dict[str, Any]] = summary.get("by_category", [])

    if income == 0 and expense == 0:
        return f"{title}\n\n📭 За этот период записей нет"

    text = f"{title}\n\n"
    text += f"📥 Доходы: +{format_amount(income)} сум\n"
    text += f"📤 Расходы: -{format_amount(expense)} сум\n"
    text += "━━━━━━━━━━━━━━━\n"

    sign = "+" if balance >= 0 else ""
    text += f"💰 Баланс: {sign}{format_amount(balance)} сум\n"

    if by_category:
        text += "\n📤 По категориям:\n"
        for cat_info in by_category:
            emoji = cat_info.get("emoji", "📦")
            name = cat_info.get("name", "Другое")
            total = cat_info.get("total", 0)
            pct = cat_info.get("percentage", 0)
            text += f"{emoji} {name}: -{format_amount(total)} ({pct}%)\n"

    return text


@router.message(Command("today"))
async def cmd_today(message: Message, **kwargs: Any) -> None:
    """Show today's financial summary."""
    session_factory = kwargs.get("session_factory")
    if not session_factory:
        return

    async with session_factory() as session:
        summary = await TransactionService.get_today_summary(
            session, message.from_user.id  # type: ignore[union-attr]
        )

    today = datetime.now()
    title = f"📊 Итоги за сегодня ({format_date_short(today)})"
    await message.reply(_build_summary_text(title, summary))


@router.message(Command("week"))
async def cmd_week(message: Message, **kwargs: Any) -> None:
    """Show this week's financial summary."""
    session_factory = kwargs.get("session_factory")
    if not session_factory:
        return

    async with session_factory() as session:
        summary = await TransactionService.get_week_summary(
            session, message.from_user.id  # type: ignore[union-attr]
        )

    title = "📊 Итоги за неделю"
    await message.reply(_build_summary_text(title, summary))


@router.message(Command("month"))
async def cmd_month(message: Message, **kwargs: Any) -> None:
    """Show this month's financial summary."""
    session_factory = kwargs.get("session_factory")
    if not session_factory:
        return

    async with session_factory() as session:
        summary = await TransactionService.get_month_summary(
            session, message.from_user.id  # type: ignore[union-attr]
        )

    title = "📊 Итоги за месяц"
    await message.reply(_build_summary_text(title, summary))
