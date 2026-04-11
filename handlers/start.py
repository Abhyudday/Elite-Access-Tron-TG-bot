"""
/start handler – user registration with deep-link referral support.
"""

import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from services.user_service import UserService
from services.referral_service import ReferralService
from bot.keyboards import main_menu_kb

logger = logging.getLogger(__name__)
router = Router(name="start")


@router.message(CommandStart(deep_link=True))
async def cmd_start_with_ref(message: Message) -> None:
    """Handle /start with a referral deep-link: /start REF_CODE"""
    if not message.from_user:
        return

    # Extract referral code from the deep-link payload
    parts = message.text.strip().split(maxsplit=1) if message.text else []
    ref_code = parts[1] if len(parts) > 1 else None

    user, created = await UserService.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        referrer_code=ref_code,
    )

    if created and user.referred_by:
        await ReferralService.record_referral(
            referrer_id=user.referred_by,
            referee_id=user.telegram_id,
        )

    greeting = "🎉 Welcome!" if created else "👋 Welcome back!"
    await message.answer(
        f"{greeting}\n\n"
        f"Your referral code: <code>{user.referral_code}</code>\n"
        f"Balance: <b>{user.balance:.4f} USDT</b>",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle plain /start (no referral code)."""
    if not message.from_user:
        return

    user, created = await UserService.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
    )

    greeting = "🎉 Welcome!" if created else "👋 Welcome back!"
    await message.answer(
        f"{greeting}\n\n"
        f"Your referral code: <code>{user.referral_code}</code>\n"
        f"Balance: <b>{user.balance:.4f} USDT</b>",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )
