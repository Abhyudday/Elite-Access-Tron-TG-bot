"""
Service for referral tracking and commission handling.
"""

import datetime
import logging
from sqlalchemy import select, func
from db.connection import get_session
from db.models import Referral, Commission, User
from config import Config

logger = logging.getLogger(__name__)


class ReferralService:

    @staticmethod
    async def record_referral(referrer_id: int, referee_id: int) -> None:
        """Store a referral relationship (idempotent)."""
        async with get_session() as session:
            exists = await session.execute(
                select(Referral).where(Referral.referee_telegram_id == referee_id)
            )
            if exists.scalar_one_or_none():
                return  # Already recorded

            ref = Referral(
                referrer_telegram_id=referrer_id,
                referee_telegram_id=referee_id,
            )
            session.add(ref)
            await session.commit()
            logger.info("Referral recorded: %s → %s", referrer_id, referee_id)

    @staticmethod
    async def process_commission(
        referrer_id: int,
        referee_id: int,
        deposit_tx_hash: str,
        deposit_amount: float,
    ) -> Commission | None:
        """
        Calculate and store (or auto-credit) a referral commission.
        Returns the Commission record, or None if no referrer.
        """
        pct = Config.REFERRAL_COMMISSION_PCT
        commission_amount = round(deposit_amount * pct / 100, 4)
        if commission_amount <= 0:
            return None

        status = "paid" if Config.AUTO_CREDIT_REFERRAL else "pending"

        async with get_session() as session:
            commission = Commission(
                referrer_telegram_id=referrer_id,
                referee_telegram_id=referee_id,
                deposit_tx_hash=deposit_tx_hash,
                amount=commission_amount,
                status=status,
                paid_at=datetime.datetime.utcnow() if status == "paid" else None,
            )
            session.add(commission)

            # Auto-credit referrer balance if configured
            if Config.AUTO_CREDIT_REFERRAL:
                result = await session.execute(
                    select(User).where(User.telegram_id == referrer_id)
                )
                referrer = result.scalar_one_or_none()
                if referrer:
                    referrer.balance += commission_amount

            await session.commit()
            logger.info(
                "Commission %s for referrer %s: $%.4f (%s)",
                commission.id, referrer_id, commission_amount, status,
            )
            return commission

    @staticmethod
    async def get_referral_count(telegram_id: int) -> int:
        async with get_session() as session:
            result = await session.execute(
                select(func.count(Referral.id)).where(
                    Referral.referrer_telegram_id == telegram_id
                )
            )
            return result.scalar_one()

    @staticmethod
    async def get_total_earnings(telegram_id: int) -> float:
        async with get_session() as session:
            result = await session.execute(
                select(func.coalesce(func.sum(Commission.amount), 0.0)).where(
                    Commission.referrer_telegram_id == telegram_id,
                    Commission.status == "paid",
                )
            )
            return float(result.scalar_one())

    @staticmethod
    async def get_pending_commissions(limit: int = 50) -> list[Commission]:
        async with get_session() as session:
            result = await session.execute(
                select(Commission)
                .where(Commission.status == "pending")
                .order_by(Commission.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_pending_commissions_with_payout(
        limit: int = 50,
    ) -> list[tuple[Commission, str | None, str | None]]:
        """
        Return list of (Commission, username, payout_address) for pending items.
        Joined with the User table so the admin has everything needed to pay out.
        """
        async with get_session() as session:
            result = await session.execute(
                select(Commission, User.username, User.payout_address)
                .join(User, User.telegram_id == Commission.referrer_telegram_id)
                .where(Commission.status == "pending")
                .order_by(Commission.created_at.asc())
                .limit(limit)
            )
            return [(row[0], row[1], row[2]) for row in result.all()]

    @staticmethod
    async def mark_commission_paid(commission_id: int) -> bool:
        async with get_session() as session:
            result = await session.execute(
                select(Commission).where(Commission.id == commission_id)
            )
            commission = result.scalar_one_or_none()
            if not commission or commission.status == "paid":
                return False

            commission.status = "paid"
            commission.paid_at = datetime.datetime.utcnow()

            # Credit referrer balance
            user_result = await session.execute(
                select(User).where(User.telegram_id == commission.referrer_telegram_id)
            )
            referrer = user_result.scalar_one_or_none()
            if referrer:
                referrer.balance += commission.amount

            await session.commit()
            logger.info("Commission %s marked paid", commission_id)
            return True
