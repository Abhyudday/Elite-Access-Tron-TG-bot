"""
Transactions handler – list recent deposit history.
"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.deposit_service import DepositService
from services.user_service import UserService
from bot.keyboards import back_menu_kb
from bot.i18n import t

logger = logging.getLogger(__name__)
router = Router(name="transactions")


@router.callback_query(F.data == "menu:transactions")
async def cb_transactions(callback: CallbackQuery) -> None:
    """Show the user's recent transactions."""
    if not callback.from_user:
        return

    user = await UserService.get_user(callback.from_user.id)
    lang = user.language if user else "en"
    txs = await DepositService.get_user_transactions(callback.from_user.id, limit=10)

    if not txs:
        text = t(lang, "no_transactions")
    else:
        lines = [t(lang, "transactions_header")]
        for tx in txs:
            short_hash = tx.tx_hash[:12] + "…"
            ts = tx.created_at.strftime("%Y-%m-%d %H:%M") if tx.created_at else "—"
            lines.append(
                f"• <code>{short_hash}</code>  "
                f"<b>{tx.amount:.4f} USDT</b>  "
                f"[{tx.status}]  {ts}"
            )
        text = "\n".join(lines)

    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=back_menu_kb()
    )
    await callback.answer()
