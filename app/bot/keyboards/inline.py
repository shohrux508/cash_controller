from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data="confirm_yes")
    builder.button(text="❌ Нет", callback_data="confirm_no")
    builder.adjust(2)
    return builder.as_markup()
