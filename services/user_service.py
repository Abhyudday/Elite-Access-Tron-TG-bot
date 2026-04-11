"""
Service for user registration and lookup.
"""

import logging
import secrets
import string

from sqlalchemy import select
from db.connection import get_session
from db.models import User

logger = logging.getLogger(__name__)


def _generate_referral_code(length: int = 8) -> str:
    """Generate a random alphanumeric referral code."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class UserService:

    @staticmethod
    async def get_or_create_user(
        telegram_id: int,
        username: str | None = None,
        referrer_code: str | None = None,
    ) -> tuple["User", bool]:
        """
        Return (user, created). If the user already exists, `created` is False.
        If `referrer_code` is provided, the referrer's telegram_id is stored.
        """
        async with get_session() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                return user, False

            # Resolve referrer
            referred_by: int | None = None
            if referrer_code:
                ref_stmt = select(User).where(User.referral_code == referrer_code)
                ref_result = await session.execute(ref_stmt)
                referrer = ref_result.scalar_one_or_none()
                if referrer and referrer.telegram_id != telegram_id:
                    referred_by = referrer.telegram_id

            # Generate unique referral code
            code = _generate_referral_code()
            while True:
                dup = await session.execute(select(User).where(User.referral_code == code))
                if dup.scalar_one_or_none() is None:
                    break
                code = _generate_referral_code()

            user = User(
                telegram_id=telegram_id,
                username=username,
                referral_code=code,
                referred_by=referred_by,
                balance=0.0,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info("New user registered: %s (ref_by=%s)", telegram_id, referred_by)
            return user, True

    @staticmethod
    async def get_user(telegram_id: int) -> User | None:
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def update_balance(telegram_id: int, delta: float) -> float:
        """Add `delta` to user balance and return new balance."""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise ValueError(f"User {telegram_id} not found")
            user.balance += delta
            await session.commit()
            await session.refresh(user)
            logger.info("Balance updated for %s: %+.4f → %.4f", telegram_id, delta, user.balance)
            return user.balance

    @staticmethod
    async def get_all_users(limit: int = 100, offset: int = 0) -> list[User]:
        async with get_session() as session:
            result = await session.execute(
                select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
            )
            return list(result.scalars().all())

    @staticmethod
    async def count_users() -> int:
        from sqlalchemy import func
        async with get_session() as session:
            result = await session.execute(select(func.count(User.telegram_id)))
            return result.scalar_one()

    @staticmethod
    async def set_payout_address(telegram_id: int, address: str) -> None:
        """Set the user's TRC20 payout wallet address."""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise ValueError(f"User {telegram_id} not found")
            user.payout_address = address
            await session.commit()
            logger.info("Payout address set for %s: %s", telegram_id, address)

    @staticmethod
    async def set_language(telegram_id: int, lang: str) -> None:
        """Set the user's preferred language ('en' or 'de')."""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                raise ValueError(f"User {telegram_id} not found")
            user.language = lang
            await session.commit()
            logger.info("Language set for %s: %s", telegram_id, lang)
