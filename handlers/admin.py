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
from services.investment_service import InvestmentService
from bot.keyboards import admin_menu_kb, commission_action_kb, commission_kb, back_menu_kb, reset_confirm_kb

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


# ── Pending commissions (payout view) ───────────────────────────────────────

@router.callback_query(F.data == "admin:pending")
async def cb_admin_pending(callback: CallbackQuery) -> None:
    if not callback.from_user or not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    rows = await ReferralService.get_pending_commissions_with_payout(limit=30)

    if not rows:
        await callback.message.edit_text(
            "✅ <b>Payouts</b>\n\nAll clear — no pending commissions!",
            parse_mode="HTML",
            reply_markup=admin_menu_kb(),
        )
        await callback.answer()
        return

    # Summary header
    total_due = sum(c.amount for c, _, _ in rows)
    header = (
        f"💸 <b>Pending Payouts</b> — {len(rows)} item(s)\n"
        f"Total due: <b>{total_due:.4f} USDT</b>\n\n"
        "Each payout is listed below ↓"
    )
    await callback.message.edit_text(
        header, parse_mode="HTML", reply_markup=admin_menu_kb()
    )

    # One message per commission so each has its own Mark as Paid button
    for commission, username, payout_address in rows:
        uname_display = f"@{username}" if username else f"ID {commission.referrer_telegram_id}"
        wallet_display = (
            f"<code>{payout_address}</code>" if payout_address
            else "⚠️ <i>No payout wallet set</i>"
        )
        text = (
            f"💰 <b>Commission #{commission.id}</b>\n"
            f"👤 Referrer: {uname_display} (<code>{commission.referrer_telegram_id}</code>)\n"
            f"💵 Amount: <b>{commission.amount:.4f} USDT</b>\n"
            f"👛 Send to: {wallet_display}\n"
            f"📅 Date: {commission.created_at.strftime('%Y-%m-%d %H:%M') if commission.created_at else '—'}\n"
            f"🔗 TX: <code>{commission.deposit_tx_hash[:16]}…</code>"
        )
        await callback.message.answer(
            text, parse_mode="HTML", reply_markup=commission_kb(commission.id)
        )

    await callback.answer()


# ── Mark commission paid ───────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:pay:"))
async def cb_admin_pay_commission(callback: CallbackQuery) -> None:
    if not callback.from_user or not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    commission_id = int(callback.data.split(":")[-1])
    success = await ReferralService.mark_commission_paid(commission_id)

    if success:
        # Update this specific message to show paid status
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.edit_text(
            callback.message.text + "\n\n✅ <b>PAID</b>",
            parse_mode="HTML",
        )
        await callback.answer("✅ Marked as paid!", show_alert=False)
    else:
        await callback.answer("⚠️ Already paid or not found.", show_alert=True)


# ── Weekly returns dashboard ─────────────────────────────────────────

@router.callback_query(F.data == "admin:weekly")
async def cb_admin_weekly(callback: CallbackQuery) -> None:
    """Show investors eligible for weekly returns with amounts and wallets."""
    if not callback.from_user or not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    investors = await InvestmentService.get_all_investors_weekly()

    if not investors:
        await callback.message.edit_text(
            "📅 <b>Weekly Returns</b>\n\n"
            "No investors with ≥ 500 USDT deposits yet.",
            parse_mode="HTML",
            reply_markup=admin_menu_kb(),
        )
        await callback.answer()
        return

    total_due = sum(i["weekly_amount"] for i in investors)
    header = (
        f"📅 <b>Weekly Returns</b> — {len(investors)} investor(s)\n"
        f"Total to pay this week: <b>{total_due:.4f} USDT</b>\n\n"
        "───────────────────────────"
    )
    await callback.message.edit_text(
        header, parse_mode="HTML", reply_markup=admin_menu_kb()
    )

    for inv in investors:
        uname = f"@{inv['username']}" if inv['username'] else f"ID {inv['telegram_id']}"
        wallet = (
            f"<code>{inv['payout_address']}</code>"
            if inv['payout_address']
            else "⚠️ <i>No payout wallet set</i>"
        )
        text = (
            f"💰 <b>{uname}</b> (<code>{inv['telegram_id']}</code>)\n"
            f"   Invested: <b>{inv['total_deposits']:.2f} USDT</b>\n"
            f"   Tier: <b>{inv['weekly_pct']:.0f}%</b> / week\n"
            f"   → Pay: <b>{inv['weekly_amount']:.4f} USDT</b>\n"
            f"   👛 Wallet: {wallet}"
        )
        await callback.message.answer(text, parse_mode="HTML")

    await callback.answer()


# ── Database reset ─────────────────────────────────────────────────

@router.callback_query(F.data == "admin:reset")
async def cb_admin_reset(callback: CallbackQuery) -> None:
    """Show confirmation warning before wiping the database."""
    if not callback.from_user or not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    await callback.message.edit_text(
        "🚨 <b>DATABASE RESET</b>\n\n"
        "⚠️ This will <b>permanently delete ALL data</b>:\n"
        "• All users\n"
        "• All deposits &amp; transactions\n"
        "• All referrals &amp; commissions\n"
        "• All weekly payouts\n\n"
        "<b>This action cannot be undone.</b>\n\n"
        "Are you sure you want to continue?",
        parse_mode="HTML",
        reply_markup=reset_confirm_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:reset_confirm")
async def cb_admin_reset_confirm(callback: CallbackQuery) -> None:
    """Actually wipe all tables after admin confirms."""
    if not callback.from_user or not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    try:
        await AdminService.reset_database()
        await callback.message.edit_text(
            "✅ <b>Database has been reset.</b>\n\n"
            "All users, deposits, referrals, commissions, and payouts have been wiped.\n"
            "The bot is now running fresh.",
            parse_mode="HTML",
            reply_markup=admin_menu_kb(),
        )
    except Exception as e:
        logger.exception("Database reset failed: %s", e)
        await callback.message.edit_text(
            f"❌ <b>Reset failed:</b> <code>{e}</code>",
            parse_mode="HTML",
            reply_markup=admin_menu_kb(),
        )
    await callback.answer()


@router.callback_query(F.data == "admin:reset_cancel")
async def cb_admin_reset_cancel(callback: CallbackQuery) -> None:
    """Cancel the reset and go back to admin panel."""
    if not callback.from_user or not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    await callback.message.edit_text(
        "🔐 <b>Admin Panel</b>\n\nDatabase reset cancelled.",
        parse_mode="HTML",
        reply_markup=admin_menu_kb(),
    )
    await callback.answer()
