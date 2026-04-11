"""
Service for managing user deposit wallet addresses.
"""

import logging
from sqlalchemy import select
from db.connection import get_session
from db.models import Deposit

logger = logging.getLogger(__name__)


class WalletService:

    @staticmethod
    async def get_or_create_address(telegram_id: int, blockchain_provider) -> str:
        """
        Return existing deposit address or generate a new one via the blockchain provider.
        `blockchain_provider` must implement `generate_address(telegram_id)`.
        """
        async with get_session() as session:
            result = await session.execute(
                select(Deposit).where(Deposit.user_telegram_id == telegram_id)
            )
            deposit = result.scalar_one_or_none()

            if deposit:
                return deposit.address

            # Generate address from blockchain provider
            address = await blockchain_provider.generate_address(telegram_id)

            deposit = Deposit(user_telegram_id=telegram_id, address=address)
            session.add(deposit)
            await session.commit()
            logger.info("Deposit address created for %s: %s", telegram_id, address)
            return address

    @staticmethod
    async def get_address_owner(address: str) -> int | None:
        """Return the telegram_id that owns this address, or None."""
        async with get_session() as session:
            result = await session.execute(
                select(Deposit).where(Deposit.address == address)
            )
            deposit = result.scalar_one_or_none()
            return deposit.user_telegram_id if deposit else None

    @staticmethod
    async def get_all_addresses() -> list[Deposit]:
        """Return all deposit records (used by deposit monitor)."""
        async with get_session() as session:
            result = await session.execute(select(Deposit))
            return list(result.scalars().all())
