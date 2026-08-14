from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Welcome message and quick usage guide."""
    text = (
        "👋 <b>Добро пожаловать в CashController!</b>\n\n"
        "Я помогу вести учёт финансов.\n"
        "Просто отправьте сумму и описание:\n\n"
        "  <code>-25 такси</code> → расход 25 000 сум\n"
        "  <code>+150 зарплата</code> → доход 150 000 сум\n"
        "  <code>-3.5 кофе</code> → расход 3 500 сум\n\n"
        "Число умножается на 1 000 автоматически.\n"
        "Категория определяется по описанию.\n\n"
        "Для списка команд: /help"
    )
    await message.reply(text)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Detailed help with all commands."""
    text = (
        "📖 <b>Как пользоваться ботом</b>\n\n"
        "<b>Быстрый ввод:</b>\n"
        "  <code>-25 такси</code> — расход 25 000\n"
        "  <code>+150 зарплата</code> — доход 150 000\n"
        "  <code>-3.5 кофе</code> — расход 3 500\n\n"
        "📊 <b>Статистика:</b>\n"
        "  /today — итоги за сегодня\n"
        "  /week — итоги за неделю\n"
        "  /month — итоги за месяц\n\n"
        "📋 <b>История:</b>\n"
        "  /history — последние 10 записей\n"
        "  /undo — отменить последнюю запись\n\n"
        "📁 <b>Категории:</b>\n"
        "  /categories — список категорий\n\n"
        "⏰ <b>Напоминания:</b>\n"
        "  /reminder 21:00 — установить\n"
        "  /reminder off — отключить\n"
        "  /reminder — проверить статус"
    )
    await message.reply(text)
