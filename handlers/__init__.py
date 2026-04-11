"""Handlers package – register all routers here."""

from aiogram import Router

from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.deposit import router as deposit_router
from handlers.referral import router as referral_router
from handlers.transactions import router as transactions_router
from handlers.wallet import router as wallet_router
from handlers.admin import router as admin_router


def get_all_routers() -> list[Router]:
    """Return all handler routers in order of priority."""
    return [
        start_router,
        menu_router,
        deposit_router,
        referral_router,
        transactions_router,
        wallet_router,
        admin_router,
    ]
