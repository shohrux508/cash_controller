from __future__ import annotations

from typing import Any

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.utils import format_amount, format_date_short
from app.services.transaction_service import TransactionService

router = Router()


@router.message(Command("history"))
async def cmd_history(message: Message, **kwargs: Any) -> None:
    """Show the last 10 transactions."""
    session_factory = kwargs.get("session_factory")
    if not session_factory or not message.from_user:
        return

    async with session_factory() as session:
        transactions = await TransactionService.get_transactions(
            session, message.from_user.id, limit=10
        )

    if not transactions:
        await message.reply("📭 История пуста")
        return

    text = "📋 Последние записи:\n\n"
    for i, tx in enumerate(transactions, 1):
        icon = "📥" if tx.type == "income" else "📤"
        sign = "+" if tx.type == "income" else "-"
        cat_display = ""
        if tx.category:
            cat_display = f" · {tx.category.emoji} {tx.category.name}"
        desc = f" · {tx.description}" if tx.description else ""
        date_str = format_date_short(tx.created_at)

        text += f"{i}. {icon} {sign}{format_amount(tx.amount)}{cat_display}{desc} · {date_str}\n"

    await message.reply(text)


@router.message(Command("undo"))
async def cmd_undo(message: Message, **kwargs: Any) -> None:
    """Delete the last transaction."""
    session_factory = kwargs.get("session_factory")
    if not session_factory or not message.from_user:
        return

    async with session_factory() as session:
        last_tx = await TransactionService.get_last_transaction(session, message.from_user.id)
        if not last_tx:
            await message.reply("❌ Нет записей для отмены")
            return

        sign = "+" if last_tx.type == "income" else "-"
        amount_str = f"{sign}{format_amount(last_tx.amount)}"
        desc = last_tx.description or "без описания"

        await TransactionService.delete_transaction(session, last_tx.id, message.from_user.id)

    await message.reply(f"♻️ Запись удалена:\n💰 {amount_str} сум · {desc}")
