"""Tests for transaction message parsing."""

from __future__ import annotations

import pytest

from app.services.transaction_service import ParsedTransaction, TransactionService


class TestParseMessage:
    """Test suite for TransactionService.parse_message."""

    def test_income_with_description(self) -> None:
        result = TransactionService.parse_message("+25 зарплата")
        assert result is not None
        assert result.type == "income"
        assert result.amount == 25_000
        assert result.description == "зарплата"

    def test_expense_with_description(self) -> None:
        result = TransactionService.parse_message("-15 такси")
        assert result is not None
        assert result.type == "expense"
        assert result.amount == 15_000
        assert result.description == "такси"

    def test_decimal_amount(self) -> None:
        result = TransactionService.parse_message("-3.5 кофе")
        assert result is not None
        assert result.type == "expense"
        assert result.amount == 3_500
        assert result.description == "кофе"

    def test_comma_decimal(self) -> None:
        result = TransactionService.parse_message("-120,5 продукты макро")
        assert result is not None
        assert result.type == "expense"
        assert result.amount == 120_500
        assert result.description == "продукты макро"

    def test_no_description(self) -> None:
        result = TransactionService.parse_message("+150")
        assert result is not None
        assert result.type == "income"
        assert result.amount == 150_000
        assert result.description == ""

    def test_whitespace_between(self) -> None:
        result = TransactionService.parse_message("-  25  обед")
        assert result is not None
        assert result.type == "expense"
        assert result.amount == 25_000
        assert result.description == "обед"

    def test_invalid_text(self) -> None:
        assert TransactionService.parse_message("hello world") is None

    def test_empty_string(self) -> None:
        assert TransactionService.parse_message("") is None

    def test_just_number(self) -> None:
        # No +/- sign → not a transaction
        assert TransactionService.parse_message("25000") is None

    def test_large_amount(self) -> None:
        result = TransactionService.parse_message("+5000 зарплата")
        assert result is not None
        assert result.type == "income"
        assert result.amount == 5_000_000

    def test_zero_amount(self) -> None:
        result = TransactionService.parse_message("+0")
        assert result is not None
        assert result.amount == 0


class TestFormatAmount:
    """Test the format_amount utility."""

    def test_format_thousands(self) -> None:
        from app.bot.utils import format_amount

        assert format_amount(25_000) == "25 000"

    def test_format_millions(self) -> None:
        from app.bot.utils import format_amount

        assert format_amount(1_500_000) == "1 500 000"

    def test_format_small(self) -> None:
        from app.bot.utils import format_amount

        assert format_amount(500) == "500"
