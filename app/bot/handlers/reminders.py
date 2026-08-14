from __future__ import annotations

import re
from typing import Any

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.services.reminder_service import ReminderService

router = Router()

TIME_PATTERN = re.compile(r"^(\d{1,2}):(\d{2})$")


@router.message(Command("reminder"))
async def cmd_reminder(message: Message, **kwargs: Any) -> None:
    """Manage reminders: set time, disable, or show status."""
    session_factory = kwargs.get("session_factory")
    if not session_factory or not message.from_user:
        return

    text = message.text or ""
    args = text.split()[1:]  # Remove /reminder

    user_id = message.from_user.id

    # /reminder — show status
    if not args:
        async with session_factory() as session:
            reminders = await ReminderService.get_user_reminders(session, user_id)

        if not reminders:
            await message.reply("⏰ Напоминания не установлены.\nУстановите: /reminder HH:MM")
            return

        r = reminders[0]
        status = "✅ Включено" if r.is_active else "❌ Выключено"
        await message.reply(f"⏰ Напоминание: {r.hour:02d}:{r.minute:02d} ({status})")
        return

    arg = args[0].strip().lower()

    # /reminder off — disable
    if arg == "off":
        async with session_factory() as session:
            reminders = await ReminderService.get_user_reminders(session, user_id)
            if reminders:
                await ReminderService.toggle_reminder(session, reminders[0].id, user_id)
                await message.reply("🔕 Напоминание отключено")
            else:
                await message.reply("⏰ У вас нет установленных напоминаний")
        return

    # /reminder HH:MM — set time
    match = TIME_PATTERN.match(arg)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            await message.reply("❌ Неверное время. Допустимо 00:00 — 23:59")
            return

        async with session_factory() as session:
            await ReminderService.set_reminder(session, user_id, hour, minute)

        await message.reply(f"✅ Напоминание установлено на {hour:02d}:{minute:02d}")
    else:
        await message.reply(
            "❌ Неверный формат.\n\n"
            "Используйте:\n"
            "  /reminder 21:00 — установить\n"
            "  /reminder off — отключить\n"
            "  /reminder — проверить статус"
        )
