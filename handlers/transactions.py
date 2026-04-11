"""
Transactions handler – list recent deposit history.
"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.deposit_service import DepositService
from bot.keyboards import back_menu_kb

logger = logging.getLogger(__name__)
router = Router(name="transactions")


@router.callback_query(F.data == "menu:transactions")
async def cb_transactions(callback: CallbackQuery) -> None:
    """Show the user's recent transactions."""
    if not callback.from_user:
        return

    txs = await DepositService.get_user_transactions(callback.from_user.id, limit=10)

    if not txs:
        text = "📋 <b>Transactions</b>\n\nNo transactions yet."
    else:
        lines = ["📋 <b>Recent Transactions</b>\n"]
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
