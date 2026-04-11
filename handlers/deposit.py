"""
Deposit handler – show the user's TRC20 deposit address.
"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.wallet_service import WalletService
from bot.keyboards import deposit_kb, back_menu_kb

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

    address = await WalletService.get_or_create_address(
        callback.from_user.id, _provider
    )

    text = (
        "📥 <b>Deposit USDT (TRC20)</b>\n\n"
        f"Send TRC20 USDT to the address below:\n\n"
        f"<code>{address}</code>\n\n"
        "⚠️ <b>Important:</b>\n"
        "• Only send <b>USDT</b> on the <b>TRC20</b> network\n"
        "• Deposits are detected automatically\n"
        "• Minimum deposit: <b>1 USDT</b>\n"
        "• You'll receive a confirmation message once credited"
    )

    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=deposit_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "wallet:export_key")
async def cb_export_key(callback: CallbackQuery) -> None:
    """Send the user their wallet private key via a separate message."""
    if not callback.from_user or not _provider:
        return

    # Only TronGridProvider supports key derivation
    from blockchain.trongrid_provider import TronGridProvider
    if not isinstance(_provider, TronGridProvider):
        await callback.answer("Key export is not available in mock mode.", show_alert=True)
        return

    priv_key = _provider._derive_private_key(callback.from_user.id)
    hex_key = priv_key.hex()

    await callback.message.answer(
        "🔐 <b>Your Wallet Private Key</b>\n\n"
        f"<tg-spoiler>{hex_key}</tg-spoiler>\n\n"
        "⚠️ <b>Keep this key secret!</b> Anyone with this key "
        "can access the funds in your deposit wallet.\n"
        "Delete this message after saving the key.",
        parse_mode="HTML",
    )
    await callback.answer()
