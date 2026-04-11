"""
Real TronGrid/TRC20 USDT blockchain provider.

Address generation: deterministic HD-style derivation using HMAC-SHA256
  (master_key + user_id → private key → TRC20 address).
  - No private keys stored in DB; rederive any time from master key.
  - Same user always gets the same address.

Deposit detection: TronGrid v1 TRC20 transfer API.

USDT TRC20 contract on mainnet: TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t
"""

import hashlib
import hmac
import logging
import aiohttp
from tronpy.keys import PrivateKey
from blockchain.base import BlockchainProvider, DepositInfo

logger = logging.getLogger(__name__)

USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
TRONGRID_BASE = "https://api.trongrid.io"


class TronGridProvider(BlockchainProvider):
    """
    Production TronGrid-backed provider.
    Requires a valid TRONGRID_API_KEY and TRON_MASTER_KEY.
    """

    def __init__(self, api_key: str, master_key: str) -> None:
        self._api_key = api_key
        self._master_key = master_key.encode() if isinstance(master_key, str) else master_key
        self._headers = {"TRON-PRO-API-KEY": api_key}

    def _derive_private_key(self, user_identifier: int) -> PrivateKey:
        """
        Deterministically derive a private key for a user using
        HMAC-SHA256(master_key, user_id). Same user always produces
        the same key — no storage needed.
        """
        derived = hmac.new(
            self._master_key,
            str(user_identifier).encode(),
            hashlib.sha256,
        ).digest()
        return PrivateKey(private_key_bytes=derived)

    async def generate_address(self, user_identifier: int) -> str:
        """
        Derive a unique TRC20 address locally (no API call required).
        The address is deterministic: same user_id + master_key → same address.
        """
        priv_key = self._derive_private_key(user_identifier)
        address = priv_key.public_key.to_base58check_address()
        logger.info("TRC20 address derived for user %s: %s", user_identifier, address)
        return address

    async def get_deposits(self, address: str) -> list[DepositInfo]:
        """
        Query TRC20 transfer events TO this address for the USDT contract.
        Returns unprocessed deposits. The caller must deduplicate via tx_hash.
        """
        deposits: list[DepositInfo] = []
        url = f"{TRONGRID_BASE}/v1/accounts/{address}/transactions/trc20"
        params = {
            "only_to": "true",
            "limit": 50,
            "contract_address": USDT_CONTRACT,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self._headers, params=params) as resp:
                    if resp.status != 200:
                        logger.error("TronGrid query failed for %s: %s", address, resp.status)
                        return deposits
                    data = await resp.json()

            for tx in data.get("data", []):
                tx_hash = tx.get("transaction_id", "")
                raw_amount = int(tx.get("value", "0"))
                # USDT has 6 decimals on TRC20
                amount = raw_amount / 1_000_000
                if amount > 0:
                    deposits.append(DepositInfo(
                        tx_hash=tx_hash,
                        to_address=address,
                        amount=amount,
                    ))

        except Exception as e:
            logger.exception("Error querying TronGrid for %s: %s", address, e)

        return deposits

    async def get_usdt_balance(self, address: str) -> float:
        """Query on-chain USDT balance via TronGrid TRC20 contract."""
        url = f"{TRONGRID_BASE}/v1/contracts/{USDT_CONTRACT}/balances"
        params = {"address": address}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self._headers, params=params) as resp:
                    if resp.status != 200:
                        return 0.0
                    data = await resp.json()
                    raw = int(data.get("balance", 0))
                    return raw / 1_000_000
        except Exception as e:
            logger.exception("Error fetching USDT balance for %s: %s", address, e)
            return 0.0
