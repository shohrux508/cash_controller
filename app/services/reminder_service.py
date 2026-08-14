from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Reminder


class ReminderService:
    @staticmethod
    async def set_reminder(session: AsyncSession, user_id: int, hour: int, minute: int) -> Reminder:
        result = await session.execute(
            select(Reminder).where(Reminder.user_id == user_id, Reminder.hour == hour, Reminder.minute == minute)
        )
        reminder = result.scalar_one_or_none()
        if reminder:
            reminder.is_active = True
            await session.commit()
            await session.refresh(reminder)
            return reminder
            
        reminder = Reminder(
            user_id=user_id,
            hour=hour,
            minute=minute,
            is_active=True
        )
        session.add(reminder)
        await session.commit()
        await session.refresh(reminder)
        return reminder

    @staticmethod
    async def get_user_reminders(session: AsyncSession, user_id: int) -> list[Reminder]:
        result = await session.execute(
            select(Reminder).where(Reminder.user_id == user_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_all_active_reminders(session: AsyncSession) -> list[Reminder]:
        result = await session.execute(
            select(Reminder)
            .options(selectinload(Reminder.user))
            .where(Reminder.is_active == True)  # noqa: E712
        )
        return list(result.scalars().all())

    @staticmethod
    async def toggle_reminder(session: AsyncSession, reminder_id: int, user_id: int) -> Reminder | None:
        result = await session.execute(
            select(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user_id)
        )
        reminder = result.scalar_one_or_none()
        if reminder:
            reminder.is_active = not reminder.is_active
            await session.commit()
            await session.refresh(reminder)
        return reminder

    @staticmethod
    async def delete_reminder(session: AsyncSession, reminder_id: int, user_id: int) -> bool:
        result = await session.execute(
            select(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user_id)
        )
        reminder = result.scalar_one_or_none()
        if reminder:
            await session.delete(reminder)
            await session.commit()
            return True
        return False
