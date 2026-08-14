from __future__ import annotations

from typing import Any

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.services.category_service import CategoryService

router = Router()


@router.message(Command("categories"))
async def cmd_categories(message: Message, **kwargs: Any) -> None:
    """List all available categories (system + custom)."""
    session_factory = kwargs.get("session_factory")
    if not session_factory or not message.from_user:
        return

    async with session_factory() as session:
        categories = await CategoryService.get_user_categories(session, message.from_user.id)

    if not categories:
        await message.reply("📭 Категории не найдены")
        return

    expense_cats = [c for c in categories if c.type == "expense"]
    income_cats = [c for c in categories if c.type == "income"]

    text = "📁 <b>Категории</b>\n\n"

    if expense_cats:
        text += "📤 <b>Расходы:</b>\n"
        for c in expense_cats:
            keywords = c.keywords[:50] + "..." if len(c.keywords) > 50 else c.keywords
            custom_tag = " (свой)" if not c.is_system else ""
            text += f"  {c.emoji} {c.name}{custom_tag}\n"
            if keywords:
                text += f"     <i>{keywords}</i>\n"

    if income_cats:
        text += "\n📥 <b>Доходы:</b>\n"
        for c in income_cats:
            keywords = c.keywords[:50] + "..." if len(c.keywords) > 50 else c.keywords
            custom_tag = " (свой)" if not c.is_system else ""
            text += f"  {c.emoji} {c.name}{custom_tag}\n"
            if keywords:
                text += f"     <i>{keywords}</i>\n"

    await message.reply(text)
