from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class TimestampMixin:
    """Mixin that adds created_at / updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )


class TransactionType(StrEnum):
    """Type of financial transaction."""

    INCOME = "income"
    EXPENSE = "expense"


class User(TimestampMixin, Base):
    """Telegram user who uses the bot."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    transactions: Mapped[list[Transaction]] = relationship(
        "Transaction", back_populates="user", cascade="all, delete-orphan"
    )
    categories: Mapped[list[Category]] = relationship(
        "Category", back_populates="user", cascade="all, delete-orphan"
    )
    reminders: Mapped[list[Reminder]] = relationship(
        "Reminder", back_populates="user", cascade="all, delete-orphan"
    )


class Category(TimestampMixin, Base):
    """Transaction category (system or user-custom)."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    emoji: Mapped[str] = mapped_column(String(10), nullable=False, default="📦")
    type: Mapped[str] = mapped_column(String(10), nullable=False, default="expense")
    keywords: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # NULL user_id = system category, available to all
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )

    user: Mapped[User | None] = relationship("User", back_populates="categories")
    transactions: Mapped[list[Transaction]] = relationship(
        "Transaction", back_populates="category"
    )


class Transaction(TimestampMixin, Base):
    """Financial transaction record (income or expense)."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")

    user: Mapped[User] = relationship("User", back_populates="transactions")
    category: Mapped[Category | None] = relationship("Category", back_populates="transactions")


class Reminder(TimestampMixin, Base):
    """User-configured reminder schedule."""

    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hour: Mapped[int] = mapped_column(Integer, nullable=False, default=21)
    minute: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    message: Mapped[str] = mapped_column(
        String(500), nullable=False, default="Не забудь записать расходы за сегодня! 📝"
    )

    user: Mapped[User] = relationship("User", back_populates="reminders")
