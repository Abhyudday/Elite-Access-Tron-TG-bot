"""
Aggregated admin statistics and queries.
"""

from services.user_service import UserService
from services.deposit_service import DepositService
from services.referral_service import ReferralService


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
