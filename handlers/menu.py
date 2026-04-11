"""
Main-menu callback handler – routes inline-button presses to sub-screens.
"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.user_service import UserService
from bot.keyboards import main_menu_kb

logger = logging.getLogger(__name__)
router = Router(name="menu")


@router.callback_query(F.data == "menu:main")
async def cb_main_menu(callback: CallbackQuery) -> None:
    """Return to the main menu."""
    if not callback.from_user:
        return
    user = await UserService.get_user(callback.from_user.id)
    balance = user.balance if user else 0.0

    await callback.message.edit_text(
        f"📋 <b>Main Menu</b>\n\nBalance: <b>{balance:.4f} USDT</b>",
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

    from bot.keyboards import back_menu_kb
    await callback.message.edit_text(
        f"💰 <b>Your Balance</b>\n\n<b>{balance:.4f} USDT</b>",
        parse_mode="HTML",
        reply_markup=back_menu_kb(),
    )
    await callback.answer()
