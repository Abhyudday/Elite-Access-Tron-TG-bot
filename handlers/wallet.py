"""
Wallet handler – set / update TRC20 payout wallet address.
Uses FSM to capture the user's text reply.
"""

import re
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.user_service import UserService
from bot.keyboards import back_menu_kb, wallet_menu_kb
from bot.i18n import t

logger = logging.getLogger(__name__)
router = Router(name="wallet")

# Simple TRC20 address regex: starts with 'T', 34 chars, base58
_TRC20_RE = re.compile(r"^T[1-9A-HJ-NP-Za-km-z]{33}$")


class WalletStates(StatesGroup):
    waiting_for_address = State()


@router.callback_query(F.data == "wallet:set_payout")
async def cb_set_payout(callback: CallbackQuery, state: FSMContext) -> None:
    """Prompt user to type their TRC20 payout address."""
    if not callback.from_user:
        return
    user = await UserService.get_user(callback.from_user.id)
    lang = user.language if user else "en"

    await callback.message.edit_text(
        t(lang, "wallet_prompt"),
        parse_mode="HTML",
        reply_markup=back_menu_kb(),
    )
    await state.set_state(WalletStates.waiting_for_address)
    await callback.answer()


@router.message(WalletStates.waiting_for_address)
async def on_payout_address(message: Message, state: FSMContext) -> None:
    """Validate and save the payout wallet address."""
    if not message.from_user or not message.text:
        return

    user = await UserService.get_user(message.from_user.id)
    lang = user.language if user else "en"
    address = message.text.strip()

    if not _TRC20_RE.match(address):
        await message.answer(
            t(lang, "wallet_invalid"),
            parse_mode="HTML",
        )
        return  # Stay in state, let them try again

    await UserService.set_payout_address(message.from_user.id, address)
    await state.clear()

    await message.answer(
        t(lang, "wallet_saved", address=address),
        parse_mode="HTML",
        reply_markup=wallet_menu_kb(),
    )
