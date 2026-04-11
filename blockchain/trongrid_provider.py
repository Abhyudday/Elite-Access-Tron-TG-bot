"""
Real TronGrid/TRC20 USDT blockchain provider.

Uses TronGrid API to:
 - Generate deposit addresses (creates new Tron accounts)
 - Query TRC20 transfer events for a given address
 - Check USDT balance

USDT TRC20 contract on mainnet: TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t
"""

import logging
import aiohttp
from blockchain.base import BlockchainProvider, DepositInfo

logger = logging.getLogger(__name__)

USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
TRONGRID_BASE = "https://api.trongrid.io"


class TronGridProvider(BlockchainProvider):
    """
    Production TronGrid-backed provider.
    Requires a valid TRONGRID_API_KEY.
    """

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._headers = {"TRON-PRO-API-KEY": api_key}

    async def generate_address(self, user_identifier: int) -> str:
        """
        Generate a new Tron account via TronGrid.
        In production, you'd typically use an HD wallet derivation
        from a master seed. This is a simplified version that calls
        the generateaddress endpoint.

        ⚠ For real production use, implement HD wallet derivation
        (e.g. using tronpy) and store private keys securely.
        """
        async with aiohttp.ClientSession() as session:
            url = f"{TRONGRID_BASE}/wallet/generateaddress"
            async with session.get(url, headers=self._headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise RuntimeError(f"TronGrid generateaddress failed: {resp.status} {text}")
                data = await resp.json()
                address = data.get("base58check") or data.get("base58")
                if not address:
                    raise RuntimeError(f"Unexpected TronGrid response: {data}")
                # ⚠ Store private_key securely (data['privateKey']) in production
                logger.info("TronGrid address generated for user %s: %s", user_identifier, address)
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
        """Query on-chain USDT balance via TronGrid."""
        url = f"{TRONGRID_BASE}/v1/accounts/{address}/transactions/trc20"
        # Simplified – in production, use the contract balanceOf call
        # This is a placeholder that sums recent incoming minus outgoing
        logger.warning("get_usdt_balance not fully implemented for TronGrid; returning 0")
        return 0.0
