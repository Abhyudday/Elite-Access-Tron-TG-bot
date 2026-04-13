"""
Investment tiers, weekly return calculations, and referral commission rates.

Weekly returns (manual, Saturday):
  500 USDT  →  5 %/week
  1000 USDT → 10 %/week
  3000 USDT → 15 %/week

Base referral commission (referrer's own total deposits):
  < 1000 USDT →  3 %
  ≥ 1000 USDT →  5 %
  ≥ 3000 USDT → 10 %

Bonus referral commission (number of referrals):
  1 referral  → +3 %
  2 referrals → +5 %
  5 referrals → +8 %

Total commission = base + bonus  (bonus applies to future referrals only)
"""

import logging
from sqlalchemy import select, func
from db.connection import get_session
from db.models import Transaction, User

logger = logging.getLogger(__name__)

# ── Tier tables (sorted highest-first for matching) ──────────────────

WEEKLY_RETURN_TIERS: list[tuple[float, float]] = [
    (3000.0, 15.0),
    (1000.0, 10.0),
    (500.0,   5.0),
]

BASE_COMMISSION_TIERS: list[tuple[float, float]] = [
    (3000.0, 10.0),
    (1000.0,  5.0),
    (0.0,     3.0),
]

BONUS_COMMISSION_TIERS: list[tuple[int, float]] = [
    (5, 8.0),
    (2, 5.0),
    (1, 3.0),
]


class InvestmentService:
    """Pure-logic helpers + DB queries for investment/commission tiers."""

    # ── Total deposits for a single user ──────────────────────────────

    @staticmethod
    async def get_total_deposits(telegram_id: int) -> float:
        """Sum of all confirmed deposits for a user."""
        async with get_session() as session:
            result = await session.execute(
                select(func.coalesce(func.sum(Transaction.amount), 0.0))
                .where(Transaction.user_telegram_id == telegram_id)
            )
            return float(result.scalar_one())

    # ── Weekly-return helpers ─────────────────────────────────────────

    @staticmethod
    def get_weekly_return_pct(total_deposits: float) -> float:
        for min_dep, pct in WEEKLY_RETURN_TIERS:
            if total_deposits >= min_dep:
                return pct
        return 0.0

    @staticmethod
    def get_weekly_return_amount(total_deposits: float) -> float:
        pct = InvestmentService.get_weekly_return_pct(total_deposits)
        return round(total_deposits * pct / 100, 4)

    # ── Commission-rate helpers ───────────────────────────────────────

    @staticmethod
    def get_base_commission_pct(referrer_total_deposits: float) -> float:
        """Base rate from referrer's own investment."""
        for min_dep, pct in BASE_COMMISSION_TIERS:
            if referrer_total_deposits >= min_dep:
                return pct
        return 3.0

    @staticmethod
    def get_bonus_commission_pct(referral_count: int) -> float:
        """Bonus rate from referrer's number of referrals."""
        for min_refs, pct in BONUS_COMMISSION_TIERS:
            if referral_count >= min_refs:
                return pct
        return 0.0

    # ── Admin: all investors eligible for weekly returns ──────────────

    @staticmethod
    async def get_all_investors_weekly() -> list[dict]:
        """
        Return investors with total_deposits ≥ 500 USDT, together with
        their tier, weekly %, weekly amount, and payout wallet.
        """
        async with get_session() as session:
            result = await session.execute(
                select(
                    User.telegram_id,
                    User.username,
                    User.payout_address,
                    func.coalesce(
                        func.sum(Transaction.amount), 0.0
                    ).label("total_deposits"),
                )
                .outerjoin(Transaction, Transaction.user_telegram_id == User.telegram_id)
                .group_by(User.telegram_id, User.username, User.payout_address)
                .having(func.coalesce(func.sum(Transaction.amount), 0.0) >= 500)
                .order_by(func.sum(Transaction.amount).desc())
            )
            rows = result.all()

        investors: list[dict] = []
        for row in rows:
            total = float(row.total_deposits)
            pct = InvestmentService.get_weekly_return_pct(total)
            investors.append({
                "telegram_id": row.telegram_id,
                "username": row.username,
                "payout_address": row.payout_address,
                "total_deposits": total,
                "weekly_pct": pct,
                "weekly_amount": round(total * pct / 100, 4),
            })
        return investors
