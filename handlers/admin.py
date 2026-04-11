"""
Admin handler – restricted to ADMIN_IDS.
Provides stats, user list, deposit list, referral list, and commission management.
"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import Config
from services.admin_service import AdminService
from services.user_service import UserService
from services.deposit_service import DepositService
from services.referral_service import ReferralService
from bot.keyboards import admin_menu_kb, commission_action_kb, back_menu_kb

logger = logging.getLogger(__name__)
router = Router(name="admin")


def _is_admin(user_id: int) -> bool:
    return user_id in Config.ADMIN_IDS


# ── /admin command ────────────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not message.from_user or not _is_admin(message.from_user.id):
        await message.answer("⛔ Unauthorized")
        return

    await message.answer(
        "🔐 <b>Admin Panel</b>",
        parse_mode="HTML",
        reply_markup=admin_menu_kb(),
    )


# ── Stats ─────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(callback: CallbackQuery) -> None:
    if not callback.from_user or not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    stats = await AdminService.get_stats()
    text = (
        "📊 <b>Bot Statistics</b>\n\n"
        f"Total users: <b>{stats['total_users']}</b>\n"
        f"Total deposits: <b>{stats['total_deposits_count']}</b> "
        f"(<b>{stats['total_deposits_amount']:.4f} USDT</b>)\n"
        f"Pending commissions: <b>{stats['pending_commissions_count']}</b> "
        f"(<b>{stats['pending_commissions_total']:.4f} USDT</b>)"
    )
    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=admin_menu_kb()
    )
    await callback.answer()


# ── Users list ────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:users")
async def cb_admin_users(callback: CallbackQuery) -> None:
    if not callback.from_user or not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    users = await UserService.get_all_users(limit=20)
    if not users:
        text = "👥 <b>Users</b>\n\nNo users yet."
    else:
        lines = ["👥 <b>Users (latest 20)</b>\n"]
        for u in users:
            uname = f"@{u.username}" if u.username else "—"
            ref = f"ref_by={u.referred_by}" if u.referred_by else "organic"
            lines.append(
                f"• <code>{u.telegram_id}</code> {uname}  "
                f"bal=<b>{u.balance:.4f}</b>  [{ref}]"
            )
        text = "\n".join(lines)

    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=admin_menu_kb()
    )
    await callback.answer()


# ── Deposits list ─────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:deposits")
async def cb_admin_deposits(callback: CallbackQuery) -> None:
    if not callback.from_user or not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    from sqlalchemy import select
    from db.connection import get_session
    from db.models import Transaction

    async with get_session() as session:
        result = await session.execute(
            select(Transaction).order_by(Transaction.created_at.desc()).limit(20)
        )
        txs = list(result.scalars().all())

    if not txs:
        text = "📥 <b>Deposits</b>\n\nNone yet."
    else:
        lines = ["📥 <b>Recent Deposits (20)</b>\n"]
        for tx in txs:
            lines.append(
                f"• user=<code>{tx.user_telegram_id}</code>  "
                f"<b>{tx.amount:.4f}</b> USDT  "
                f"tx=<code>{tx.tx_hash[:12]}…</code>  [{tx.status}]"
            )
        text = "\n".join(lines)

    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=admin_menu_kb()
    )
    await callback.answer()


# ── Referrals list ────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:referrals")
async def cb_admin_referrals(callback: CallbackQuery) -> None:
    if not callback.from_user or not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    from sqlalchemy import select
    from db.connection import get_session
    from db.models import Referral

    async with get_session() as session:
        result = await session.execute(
            select(Referral).order_by(Referral.created_at.desc()).limit(20)
        )
        refs = list(result.scalars().all())

    if not refs:
        text = "👥 <b>Referrals</b>\n\nNone yet."
    else:
        lines = ["👥 <b>Recent Referrals (20)</b>\n"]
        for r in refs:
            lines.append(
                f"• {r.referrer_telegram_id} → {r.referee_telegram_id}"
            )
        text = "\n".join(lines)

    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=admin_menu_kb()
    )
    await callback.answer()


# ── Pending commissions ──────────────────────────────────────────────

@router.callback_query(F.data == "admin:pending")
async def cb_admin_pending(callback: CallbackQuery) -> None:
    if not callback.from_user or not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    commissions = await ReferralService.get_pending_commissions(limit=20)
    if not commissions:
        await callback.message.edit_text(
            "⏳ <b>Pending Commissions</b>\n\nAll clear — nothing pending!",
            parse_mode="HTML",
            reply_markup=admin_menu_kb(),
        )
        await callback.answer()
        return

    lines = ["⏳ <b>Pending Commissions</b>\n"]
    for c in commissions:
        lines.append(
            f"• ID={c.id}  referrer=<code>{c.referrer_telegram_id}</code>  "
            f"<b>{c.amount:.4f} USDT</b>  tx=<code>{c.deposit_tx_hash[:12]}…</code>"
        )
    text = "\n".join(lines)

    # Show pay button for the first pending commission
    await callback.message.edit_text(
        text, parse_mode="HTML",
        reply_markup=commission_action_kb(commissions[0].id),
    )
    await callback.answer()


# ── Mark commission paid ──────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:pay:"))
async def cb_admin_pay_commission(callback: CallbackQuery) -> None:
    if not callback.from_user or not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    commission_id = int(callback.data.split(":")[-1])
    success = await ReferralService.mark_commission_paid(commission_id)

    if success:
        await callback.answer("✅ Commission marked as paid and credited!", show_alert=True)
    else:
        await callback.answer("⚠️ Commission not found or already paid.", show_alert=True)

    # Refresh the pending list
    await cb_admin_pending(callback)
