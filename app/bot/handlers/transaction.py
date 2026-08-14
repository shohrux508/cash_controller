from __future__ import annotations

from typing import Any

from aiogram import Router
from aiogram.types import Message

from app.bot.utils import format_amount, format_date
from app.services.category_service import CategoryService
from app.services.transaction_service import TransactionService

router = Router()


@router.message()
async def process_transaction(message: Message, **kwargs: Any) -> None:
    """Parse free-text messages like '+25 такси' and record a transaction."""
    text = message.text
    if not text or not message.from_user:
        return

    parsed = TransactionService.parse_message(text)
    if not parsed:
        return  # Not a transaction, ignore silently

    session_factory = kwargs.get("session_factory")
    if not session_factory:
        bot = kwargs.get("bot")
        if bot:
            session_factory = bot["session_factory"]
        else:
            return

    async with session_factory() as session:
        category = await CategoryService.detect_category(
            session, parsed.description, message.from_user.id, parsed.type
        )
        transaction = await TransactionService.create_transaction(
            session,
            user_id=message.from_user.id,
            amount=parsed.amount,
            tx_type=parsed.type,
            description=parsed.description,
            category_id=category.id if category else None,
        )

        cat_display = f"{category.emoji} {category.name}" if category else "📦 Без категории"
        type_str = "Доход записан" if parsed.type == "income" else "Расход записан"
        sign = "+" if parsed.type == "income" else "-"

        reply_text = (
            f"✅ {type_str}\n\n"
            f"💰 {sign}{format_amount(parsed.amount)} сум\n"
            f"📁 {cat_display}\n"
        )
        if parsed.description:
            reply_text += f"📝 {parsed.description}\n"
        reply_text += f"📅 {format_date(transaction.created_at)}"

        await message.reply(reply_text)
