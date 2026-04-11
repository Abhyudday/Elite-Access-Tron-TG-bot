"""
Inline keyboard builders for the Telegram bot UI.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_kb() -> InlineKeyboardMarkup:
    """Primary menu shown after /start and on 'Back to menu'."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 Balance", callback_data="menu:balance"),
            InlineKeyboardButton(text="📥 Deposit", callback_data="menu:deposit"),
        ],
        [
            InlineKeyboardButton(text="👥 Referral", callback_data="menu:referral"),
            InlineKeyboardButton(text="📋 Transactions", callback_data="menu:transactions"),
        ],
    ])


def back_menu_kb() -> InlineKeyboardMarkup:
    """Single 'Back' button returning to the main menu."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu:main")],
    ])


def deposit_kb() -> InlineKeyboardMarkup:
    """Deposit screen keyboard with Export Key and Back buttons."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Export Wallet Key", callback_data="wallet:export_key")],
        [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu:main")],
    ])


def admin_menu_kb() -> InlineKeyboardMarkup:
    """Admin panel inline keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Stats", callback_data="admin:stats"),
            InlineKeyboardButton(text="👥 Users", callback_data="admin:users"),
        ],
        [
            InlineKeyboardButton(text="📥 Deposits", callback_data="admin:deposits"),
            InlineKeyboardButton(text="👥 Referrals", callback_data="admin:referrals"),
        ],
        [
            InlineKeyboardButton(text="⏳ Pending Commissions", callback_data="admin:pending"),
        ],
    ])


def commission_action_kb(commission_id: int) -> InlineKeyboardMarkup:
    """Mark a single commission as paid."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Mark Paid",
                callback_data=f"admin:pay:{commission_id}",
            ),
        ],
    ])
