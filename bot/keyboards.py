"""
Inline keyboard builders for the Telegram bot UI.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


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
        [
            InlineKeyboardButton(text="👛 Wallet", callback_data="menu:wallet"),
            InlineKeyboardButton(text="🌐 Language", callback_data="menu:language"),
        ],
    ])


def back_menu_kb() -> InlineKeyboardMarkup:
    """Single 'Back' button returning to the main menu."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu:main")],
    ])


def language_kb() -> InlineKeyboardMarkup:
    """Language selection keyboard shown on first /start."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="lang:de"),
        ],
    ])


def wallet_menu_kb() -> InlineKeyboardMarkup:
    """Wallet settings keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="� Set Payout Wallet", callback_data="wallet:set_payout")],
        [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu:main")],
    ])


def referral_kb() -> InlineKeyboardMarkup:
    """Referral screen keyboard with a copy-link shortcut."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Copy Referral Link", callback_data="copy:ref_link")],
        [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu:main")],
    ])


def deposit_copy_kb() -> InlineKeyboardMarkup:
    """Deposit screen keyboard with a copy-address shortcut."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Copy Deposit Address", callback_data="copy:dep_addr")],
        [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu:main")],
    ])


def commission_kb(commission_id: int) -> InlineKeyboardMarkup:
    """Per-commission keyboard shown in admin payout view."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Mark as Paid",
                callback_data=f"admin:pay:{commission_id}",
            ),
        ],
        [InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin:pending")],
    ])


def admin_menu_kb() -> InlineKeyboardMarkup:
    """Admin panel inline keyboard with large full-width buttons."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 View Bot Statistics", callback_data="admin:stats")],
            [InlineKeyboardButton(text="👥 View All Users", callback_data="admin:users")],
            [InlineKeyboardButton(text="📥 View Deposit History", callback_data="admin:deposits")],
            [InlineKeyboardButton(text="👥 View Referral List", callback_data="admin:referrals")],
            [InlineKeyboardButton(text="💸 Pay Referral Commissions", callback_data="admin:pending")],
            [InlineKeyboardButton(text="📅 Pay Weekly Returns", callback_data="admin:weekly")],
        ]
    )


def commission_action_kb(commission_id: int) -> InlineKeyboardMarkup:
    """Mark a single commission as paid (legacy, kept for compat)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Mark Paid",
                callback_data=f"admin:pay:{commission_id}",
            ),
        ],
    ])
