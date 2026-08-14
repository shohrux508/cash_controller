from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Category, Transaction, TransactionType


@dataclass
class ParsedTransaction:
    type: str
    amount: int
    description: str


class TransactionService:
    # Pattern: ^([+-])\s*(\d+(?:\.\d+)?)\s*(.*)$
    PARSE_REGEX = re.compile(r"^([+-])\s*(\d+(?:[.,]\d+)?)\s*(.*)$")

    @staticmethod
    def parse_message(text: str) -> ParsedTransaction | None:
        text = text.strip()
        match = TransactionService.PARSE_REGEX.match(text)
        if not match:
            return None
            
        sign, amount_str, description = match.groups()
        tx_type = TransactionType.INCOME if sign == "+" else TransactionType.EXPENSE
        
        amount_float = float(amount_str.replace(",", "."))
        amount_int = int(amount_float * 1000)
        
        return ParsedTransaction(
            type=tx_type,
            amount=amount_int,
            description=description.strip()
        )

    @staticmethod
    async def create_transaction(
        session: AsyncSession, user_id: int, amount: int, tx_type: str, description: str, category_id: int | None
    ) -> Transaction:
        tx = Transaction(
            user_id=user_id,
            amount=amount,
            type=tx_type,
            description=description,
            category_id=category_id
        )
        session.add(tx)
        await session.commit()
        await session.refresh(tx)
        return tx

    @staticmethod
    async def delete_transaction(session: AsyncSession, transaction_id: int, user_id: int) -> bool:
        result = await session.execute(
            select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == user_id)
        )
        tx = result.scalar_one_or_none()
        if tx:
            await session.delete(tx)
            await session.commit()
            return True
        return False

    @staticmethod
    async def get_last_transaction(session: AsyncSession, user_id: int) -> Transaction | None:
        result = await session.execute(
            select(Transaction)
            .options(selectinload(Transaction.category))
            .where(Transaction.user_id == user_id)
            .order_by(desc(Transaction.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_transactions(
        session: AsyncSession, user_id: int, limit: int = 10, offset: int = 0
    ) -> list[Transaction]:
        result = await session.execute(
            select(Transaction)
            .options(selectinload(Transaction.category))
            .where(Transaction.user_id == user_id)
            .order_by(desc(Transaction.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_period_summary(
        session: AsyncSession, user_id: int, start_date: datetime, end_date: datetime
    ) -> dict:
        result = await session.execute(
            select(Transaction, Category)
            .outerjoin(Category, Transaction.category_id == Category.id)
            .where(
                Transaction.user_id == user_id,
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date,
            )
        )
        rows = result.all()
        
        income = 0
        expense = 0
        by_category_dict = {}
        
        for tx, cat in rows:
            if tx.type == TransactionType.INCOME:
                income += tx.amount
            else:
                expense += tx.amount
                
                cat_name = cat.name if cat else "Без категории"
                cat_emoji = cat.emoji if cat else "❓"
                cat_id = cat.id if cat else 0
                
                if cat_id not in by_category_dict:
                    by_category_dict[cat_id] = {
                        "name": cat_name,
                        "emoji": cat_emoji,
                        "total": 0,
                    }
                by_category_dict[cat_id]["total"] += tx.amount

        by_category = []
        for val in by_category_dict.values():
            percentage = (val["total"] / expense * 100) if expense > 0 else 0
            val["percentage"] = round(percentage, 1)
            by_category.append(val)
            
        by_category.sort(key=lambda x: x["total"], reverse=True)

        return {
            "income": income,
            "expense": expense,
            "balance": income - expense,
            "by_category": by_category
        }

    @staticmethod
    async def get_today_summary(session: AsyncSession, user_id: int) -> dict:
        now = datetime.now()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return await TransactionService.get_period_summary(session, user_id, start, end)

    @staticmethod
    async def get_week_summary(session: AsyncSession, user_id: int) -> dict:
        now = datetime.now()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=now.weekday())
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return await TransactionService.get_period_summary(session, user_id, start, end)

    @staticmethod
    async def get_month_summary(session: AsyncSession, user_id: int) -> dict:
        now = datetime.now()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return await TransactionService.get_period_summary(session, user_id, start, end)
