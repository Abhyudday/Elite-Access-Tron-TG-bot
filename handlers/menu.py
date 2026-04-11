"""
Main-menu callback handler – routes inline-button presses to sub-screens.
"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.user_service import UserService
from bot.keyboards import main_menu_kb, back_menu_kb, wallet_menu_kb
from bot.i18n import t

logger = logging.getLogger(__name__)
router = Router(name="menu")


@router.callback_query(F.data == "menu:main")
async def cb_main_menu(callback: CallbackQuery) -> None:
    """Return to the main menu."""
    if not callback.from_user:
        return
    user = await UserService.get_user(callback.from_user.id)
    balance = user.balance if user else 0.0
    lang = user.language if user else "en"

    await callback.message.edit_text(
        t(lang, "main_menu", balance=f"{balance:.4f}"),
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:balance")
async def cb_balance(callback: CallbackQuery) -> None:
    """Show current balance."""
    if not callback.from_user:
        return
    user = await UserService.get_user(callback.from_user.id)
    balance = user.balance if user else 0.0
    lang = user.language if user else "en"

    await callback.message.edit_text(
        t(lang, "balance", balance=f"{balance:.4f}"),
        parse_mode="HTML",
        reply_markup=back_menu_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:wallet")
async def cb_wallet(callback: CallbackQuery) -> None:
    """Show wallet settings with payout address."""
    if not callback.from_user:
        return
    user = await UserService.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Please /start first.", show_alert=True)
        return
    lang = user.language or "en"
    payout = f"<code>{user.payout_address}</code>" if user.payout_address else t(lang, "wallet_not_set")

    await callback.message.edit_text(
        t(lang, "wallet", payout_display=payout),
        parse_mode="HTML",
        reply_markup=wallet_menu_kb(),
    )
    await callback.answer()
