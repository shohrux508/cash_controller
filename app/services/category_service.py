from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Category, TransactionType


class CategoryService:
    SYSTEM_CATEGORIES = [
        {"name": "🍔 Еда", "emoji": "🍔", "type": TransactionType.EXPENSE, "keywords": "еда, продукты, макро, обед, ужин, завтрак, кафе, ресторан, магазин, хлеб, мясо, молоко, фрукты, овощи"},
        {"name": "🚕 Транспорт", "emoji": "🚕", "type": TransactionType.EXPENSE, "keywords": "такси, яндекс, бензин, метро, автобус, uber, маршрутка"},
        {"name": "🏠 Жильё", "emoji": "🏠", "type": TransactionType.EXPENSE, "keywords": "аренда, квартира, коммуналка, ком, ремонт, мебель"},
        {"name": "👕 Одежда", "emoji": "👕", "type": TransactionType.EXPENSE, "keywords": "одежда, обувь, шмотки, куртка, джинсы"},
        {"name": "💊 Здоровье", "emoji": "💊", "type": TransactionType.EXPENSE, "keywords": "аптека, лекарства, врач, клиника, больница, стоматолог"},
        {"name": "📱 Связь", "emoji": "📱", "type": TransactionType.EXPENSE, "keywords": "телефон, интернет, связь, мобильный"},
        {"name": "🎮 Развлечения", "emoji": "🎮", "type": TransactionType.EXPENSE, "keywords": "кино, игра, подписка, netflix, spotify, развлечения"},
        {"name": "💼 Зарплата", "emoji": "💼", "type": TransactionType.INCOME, "keywords": "зарплата, зп, аванс, фриланс, доход, перевод"},
        {"name": "📦 Другое", "emoji": "📦", "type": TransactionType.EXPENSE, "keywords": ""},
        {"name": "📦 Другое", "emoji": "📦", "type": TransactionType.INCOME, "keywords": ""},
    ]

    @staticmethod
    async def seed_default_categories(session: AsyncSession) -> None:
        result = await session.execute(select(Category).where(Category.is_system == True))
        existing_categories = result.scalars().all()
        if existing_categories:
            return
            
        for cat_data in CategoryService.SYSTEM_CATEGORIES:
            cat = Category(
                name=cat_data["name"],
                emoji=cat_data["emoji"],
                type=cat_data["type"],
                keywords=cat_data["keywords"],
                is_system=True,
                user_id=None,
            )
            session.add(cat)
        
        await session.commit()

    @staticmethod
    async def get_user_categories(session: AsyncSession, user_id: int) -> list[Category]:
        result = await session.execute(
            select(Category).where(
                (Category.user_id == user_id) | (Category.is_system == True)
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def create_custom_category(
        session: AsyncSession, user_id: int, name: str, emoji: str, type: str, keywords: str
    ) -> Category:
        category = Category(
            name=name,
            emoji=emoji,
            type=type,
            keywords=keywords,
            is_system=False,
            user_id=user_id,
        )
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category

    @staticmethod
    async def detect_category(
        session: AsyncSession, text: str, user_id: int, tx_type: str
    ) -> Category | None:
        categories = await CategoryService.get_user_categories(session, user_id)
        
        # Filter by type
        type_categories = [c for c in categories if c.type == tx_type]
        
        # Order matters: custom first, then system
        custom_cats = [c for c in type_categories if not c.is_system]
        system_cats = [c for c in type_categories if c.is_system]
        
        text_lower = text.lower()
        
        for cat in custom_cats:
            keywords = [kw.strip().lower() for kw in cat.keywords.split(",") if kw.strip()]
            for kw in keywords:
                if kw in text_lower:
                    return cat
                    
        for cat in system_cats:
            keywords = [kw.strip().lower() for kw in cat.keywords.split(",") if kw.strip()]
            for kw in keywords:
                if kw in text_lower:
                    return cat
                    
        # Fallback to "Другое"
        fallback = next((c for c in system_cats if "Другое" in c.name), None)
        if fallback:
            return fallback
            
        return type_categories[0] if type_categories else None
