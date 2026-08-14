from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


class UserService:
    @staticmethod
    async def get_or_create_user(
        session: AsyncSession, telegram_id: int, username: str | None, full_name: str
    ) -> User:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

        if user:
            # Update info if changed
            if user.username != username or user.full_name != full_name:
                user.username = username
                user.full_name = full_name
                await session.commit()
                await session.refresh(user)
            return user

        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def is_authorized(telegram_id: int, admin_ids: list[int]) -> bool:
        return telegram_id in admin_ids
