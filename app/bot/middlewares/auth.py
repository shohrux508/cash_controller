from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from app.core.config import settings
from app.services.user_service import UserService


class AuthMiddleware(BaseMiddleware):
    """Check if the user is in the admin whitelist and auto-register."""

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if not event.from_user:
            return

        telegram_id = event.from_user.id

        if telegram_id not in settings.admin_chat_ids:
            await event.reply("⛔ Доступ запрещён")
            return

        bot = data["bot"]
        session_factory = bot["session_factory"]

        async with session_factory() as session:
            user = await UserService.get_or_create_user(
                session,
                telegram_id,
                event.from_user.username,
                event.from_user.full_name,
            )
            data["user"] = user
            data["session_factory"] = session_factory

        return await handler(event, data)
