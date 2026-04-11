"""
/start handler – user registration with deep-link referral support.
New users see a language selection first, then a welcome explanation.
"""

import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from services.user_service import UserService
from services.referral_service import ReferralService
from bot.keyboards import main_menu_kb, language_kb
from bot.i18n import t

logger = logging.getLogger(__name__)
router = Router(name="start")

# Temporary in-memory store for referral codes pending language selection
_pending_referrals: dict[int, str | None] = {}


def _welcome_text(user, created: bool, lang: str) -> str:
    """Build the welcome or welcome-back message text."""
    key = "welcome_new" if created else "welcome_back"
    return t(lang, key,
             referral_code=user.referral_code,
             balance=f"{user.balance:.4f}")


@router.message(CommandStart(deep_link=True))
async def cmd_start_with_ref(message: Message) -> None:
    """Handle /start with a referral deep-link: /start REF_CODE"""
    if not message.from_user:
        return

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

    if created:
        _pending_referrals[message.from_user.id] = ref_code
        await message.answer(
            t("en", "choose_language"),
            parse_mode="HTML",
            reply_markup=language_kb(),
        )
    else:
        lang = user.language or "en"
        await message.answer(
            _welcome_text(user, False, lang),
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

    if created:
        _pending_referrals[message.from_user.id] = None
        await message.answer(
            t("en", "choose_language"),
            parse_mode="HTML",
            reply_markup=language_kb(),
        )
    else:
        lang = user.language or "en"
        await message.answer(
            _welcome_text(user, False, lang),
            parse_mode="HTML",
            reply_markup=main_menu_kb(),
        )


@router.callback_query(F.data.startswith("lang:"))
async def cb_language_select(callback: CallbackQuery) -> None:
    """Handle language selection callback."""
    if not callback.from_user:
        return

    lang = callback.data.split(":")[1]  # 'en' or 'de'
    if lang not in ("en", "de"):
        lang = "en"

    await UserService.set_language(callback.from_user.id, lang)
    _pending_referrals.pop(callback.from_user.id, None)

    user = await UserService.get_user(callback.from_user.id)
    if not user:
        return

    text = _welcome_text(user, True, lang)
    # Edit the language-selection message into the welcome message
    await callback.message.edit_text(
        f"{t(lang, 'language_set')}\n\n{text}",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()
