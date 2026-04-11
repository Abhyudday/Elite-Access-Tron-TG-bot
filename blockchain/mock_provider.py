"""
Mock blockchain provider for local testing without real blockchain.

Simulates address generation and allows injecting fake deposits
via the `simulate_deposit` method.
"""

import hashlib
import logging
import secrets
from blockchain.base import BlockchainProvider, DepositInfo

logger = logging.getLogger(__name__)


class MockBlockchainProvider(BlockchainProvider):
    """
    In-memory mock. Useful for development and automated tests.
    Call `simulate_deposit(address, amount)` to inject a fake deposit.
    """

    def __init__(self) -> None:
        # address → list of pending DepositInfo
        self._pending_deposits: dict[str, list[DepositInfo]] = {}
        self._balances: dict[str, float] = {}

    async def generate_address(self, user_identifier: int) -> str:
        """Deterministic fake TRC20 address based on user id."""
        raw = hashlib.sha256(f"mock-trc20-{user_identifier}".encode()).hexdigest()
        address = "T" + raw[:33].upper()
        self._balances.setdefault(address, 0.0)
        logger.debug("Mock address generated for %s: %s", user_identifier, address)
        return address

    async def get_deposits(self, address: str) -> list[DepositInfo]:
        """Return and clear any simulated pending deposits for this address."""
        deposits = self._pending_deposits.pop(address, [])
        return deposits

    async def get_usdt_balance(self, address: str) -> float:
        return self._balances.get(address, 0.0)

    # ── Test helpers ──────────────────────────────────────────────────

    def simulate_deposit(self, address: str, amount: float) -> str:
        """
        Inject a fake deposit. Returns the fake tx_hash.
        The next call to `get_deposits(address)` will return it.
        """
        tx_hash = secrets.token_hex(32)
        info = DepositInfo(tx_hash=tx_hash, to_address=address, amount=amount)
        self._pending_deposits.setdefault(address, []).append(info)
        self._balances[address] = self._balances.get(address, 0.0) + amount
        logger.info("Mock deposit simulated: %s → %s (%.4f USDT)", tx_hash[:16], address[:16], amount)
        return tx_hash
