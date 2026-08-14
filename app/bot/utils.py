from __future__ import annotations

from datetime import datetime

MONTHS_RU = {
    1: "янв", 2: "фев", 3: "мар", 4: "апр",
    5: "мая", 6: "июн", 7: "июл", 8: "авг",
    9: "сен", 10: "окт", 11: "ноя", 12: "дек",
}


def format_amount(amount: int) -> str:
    """Format amount with space thousands separator, no sign: 25000 → '25 000'."""
    return f"{amount:,}".replace(",", " ")


def format_amount_signed(amount: int, tx_type: str) -> str:
    """Format with sign: income → '+25 000', expense → '-25 000'."""
    sign = "+" if tx_type == "income" else "-"
    return f"{sign}{format_amount(amount)}"


def format_date(dt: datetime) -> str:
    """Format as '12 авг 2026'."""
    return f"{dt.day} {MONTHS_RU[dt.month]} {dt.year}"


def format_date_short(dt: datetime) -> str:
    """Format as '12 авг'."""
    return f"{dt.day} {MONTHS_RU[dt.month]}"
