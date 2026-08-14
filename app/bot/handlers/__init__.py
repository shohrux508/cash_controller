from __future__ import annotations

from aiogram import Router

from .categories import router as categories_router
from .history import router as history_router
from .reminders import router as reminders_router
from .start import router as start_router
from .stats import router as stats_router
from .transaction import router as transaction_router

main_router = Router()
main_router.include_router(start_router)
main_router.include_router(stats_router)
main_router.include_router(history_router)
main_router.include_router(categories_router)
main_router.include_router(reminders_router)
# Transaction handler MUST be last — it catches all unhandled text messages
main_router.include_router(transaction_router)
