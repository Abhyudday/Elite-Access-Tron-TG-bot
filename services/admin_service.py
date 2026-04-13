"""
Aggregated admin statistics and queries.
"""

import logging
from sqlalchemy import text
from db.connection import get_session
from services.user_service import UserService
from services.deposit_service import DepositService
from services.referral_service import ReferralService

logger = logging.getLogger(__name__)


class AdminService:

    @staticmethod
    async def get_stats() -> dict:
        total_users = await UserService.count_users()
        total_deposits_amount = await DepositService.get_total_deposits()
        total_deposits_count = await DepositService.count_deposits()
        pending_commissions = await ReferralService.get_pending_commissions(limit=1000)
        pending_total = sum(c.amount for c in pending_commissions)

        return {
            "total_users": total_users,
            "total_deposits_amount": total_deposits_amount,
            "total_deposits_count": total_deposits_count,
            "pending_commissions_count": len(pending_commissions),
            "pending_commissions_total": round(pending_total, 4),
        }

    @staticmethod
    async def reset_database() -> None:
        """Truncate all application tables so the bot starts fresh."""
        tables = [
            "weekly_payouts",
            "commissions",
            "transactions",
            "referrals",
            "deposits",
            "users",
        ]
        async with get_session() as session:
            for table in tables:
                await session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
            await session.commit()
        logger.warning("DATABASE RESET: all tables truncated by admin")
