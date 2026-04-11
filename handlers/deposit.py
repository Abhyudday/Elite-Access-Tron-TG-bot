"""
Deposit handler – show the user's TRC20 deposit address.
"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.wallet_service import WalletService
from services.user_service import UserService
from bot.keyboards import deposit_copy_kb, back_menu_kb
from bot.i18n import t

_last_dep_address: dict[int, str] = {}

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

    _last_dep_address[callback.from_user.id] = address
    text = t(lang, "deposit", address=address)

    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=deposit_copy_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "copy:dep_addr")
async def cb_copy_dep_addr(callback: CallbackQuery) -> None:
    """Send the deposit address as a standalone tappable message."""
    if not callback.from_user or not _provider:
        return
    address = _last_dep_address.get(callback.from_user.id)
    if not address:
        address = await WalletService.get_or_create_address(callback.from_user.id, _provider)
    await callback.message.answer(f"<code>{address}</code>", parse_mode="HTML")
    await callback.answer("Tap the address above to copy 💆", show_alert=False)
