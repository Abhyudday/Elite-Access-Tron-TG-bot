"""
Deposit handler – show the user's TRC20 deposit address.
"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.wallet_service import WalletService
from services.user_service import UserService
from bot.keyboards import back_menu_kb
from bot.i18n import t

logger = logging.getLogger(__name__)
router = Router(name="deposit")

# The blockchain provider is injected at startup via router's `provider` attribute
_provider = None


def set_provider(provider) -> None:
    global _provider
    _provider = provider


@router.callback_query(F.data == "menu:deposit")
async def cb_deposit(callback: CallbackQuery) -> None:
    """Display the user's unique deposit address with instructions."""
    if not callback.from_user:
        return

    user = await UserService.get_user(callback.from_user.id)
    lang = user.language if user else "en"

    address = await WalletService.get_or_create_address(
        callback.from_user.id, _provider
    )

    text = t(lang, "deposit", address=address)

    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=back_menu_kb()
    )
    await callback.answer()
