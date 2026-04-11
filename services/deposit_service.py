"""
Service for recording deposits and crediting user balances.
"""

import logging
from sqlalchemy import select, func
from db.connection import get_session
from db.models import Transaction

logger = logging.getLogger(__name__)


class DepositService:

    @staticmethod
    async def tx_exists(tx_hash: str) -> bool:
        """Check if a transaction hash has already been recorded."""
        async with get_session() as session:
            result = await session.execute(
                select(Transaction).where(Transaction.tx_hash == tx_hash)
            )
            return result.scalar_one_or_none() is not None

    @staticmethod
    async def record_deposit(
        telegram_id: int, tx_hash: str, amount: float, status: str = "confirmed"
    ) -> Transaction:
        """Insert a new transaction record."""
        async with get_session() as session:
            tx = Transaction(
                user_telegram_id=telegram_id,
                tx_hash=tx_hash,
                amount=amount,
                status=status,
            )
            session.add(tx)
            await session.commit()
            await session.refresh(tx)
            logger.info("Deposit recorded: user=%s tx=%s amt=%.4f", telegram_id, tx_hash, amount)
            return tx

    @staticmethod
    async def get_user_transactions(telegram_id: int, limit: int = 20) -> list[Transaction]:
        async with get_session() as session:
            result = await session.execute(
                select(Transaction)
                .where(Transaction.user_telegram_id == telegram_id)
                .order_by(Transaction.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_total_deposits() -> float:
        async with get_session() as session:
            result = await session.execute(
                select(func.coalesce(func.sum(Transaction.amount), 0.0))
            )
            return float(result.scalar_one())

    @staticmethod
    async def count_deposits() -> int:
        async with get_session() as session:
            result = await session.execute(select(func.count(Transaction.id)))
            return result.scalar_one()
