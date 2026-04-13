"""
Abstract blockchain provider interface.
All concrete providers (mock, TronGrid, etc.) must implement this.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DepositInfo:
    """Represents a single detected on-chain deposit."""
    tx_hash: str
    to_address: str
    amount: float  # USDT amount
    confirmations: int = 1


class BlockchainProvider(ABC):
    """
    Abstract interface for TRC20 USDT blockchain operations.
    Swap this out to switch between mock, TronGrid, or any third-party service.
    """

    @abstractmethod
    async def generate_address(self, user_identifier: int) -> str:
        """Generate (or derive) a unique TRC20 deposit address for a user."""
        ...

    @abstractmethod
    async def get_deposits(self, address: str) -> list[DepositInfo]:
        """
        Return new/unprocessed USDT deposits to `address`.
        The monitor calls this periodically for every tracked address.
        """
        ...

    @abstractmethod
    async def get_usdt_balance(self, address: str) -> float:
        """Return the current USDT balance of an address."""
        ...

    async def transfer_usdt(
        self, from_user_identifier: int, to_address: str, amount: float,
    ) -> str | None:
        """
        Transfer USDT from a user's derived deposit wallet to `to_address`.
        Returns the tx_hash on success, or None on failure.
        Override in providers that support on-chain transfers.
        """
        return None  # default: not supported
