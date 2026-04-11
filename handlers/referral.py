"""
Referral handler – show referral link, stats, and earnings.
"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.user_service import UserService
from services.referral_service import ReferralService
from bot.keyboards import back_menu_kb
from bot.i18n import t

logger = logging.getLogger(__name__)
router = Router(name="referral")


@router.callback_query(F.data == "menu:referral")
async def cb_referral(callback: CallbackQuery) -> None:
    """Display referral link, invite count, and earnings."""
    if not callback.from_user:
        return

    user = await UserService.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Please /start first.", show_alert=True)
        return

    # Fetch the bot's username for the deep-link
    bot_info = await callback.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user.referral_code}"

    lang = user.language or "en"
    ref_count = await ReferralService.get_referral_count(user.telegram_id)
    total_earned = await ReferralService.get_total_earnings(user.telegram_id)

    text = t(lang, "referral",
             ref_link=ref_link,
             referral_code=user.referral_code,
             ref_count=ref_count,
             total_earned=f"{total_earned:.4f}")

    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=back_menu_kb()
    )
    await callback.answer()
