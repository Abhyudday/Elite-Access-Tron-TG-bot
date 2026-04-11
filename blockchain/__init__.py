from blockchain.base import BlockchainProvider, DepositInfo
from blockchain.mock_provider import MockBlockchainProvider
from blockchain.trongrid_provider import TronGridProvider
from config import Config


def get_blockchain_provider() -> BlockchainProvider:
    """Factory: return the configured blockchain provider."""
    if Config.BLOCKCHAIN_PROVIDER == "trongrid":
        if not Config.TRON_MASTER_KEY:
            raise ValueError("TRON_MASTER_KEY is required when BLOCKCHAIN_PROVIDER=trongrid")
        return TronGridProvider(api_key=Config.TRONGRID_API_KEY, master_key=Config.TRON_MASTER_KEY)
    return MockBlockchainProvider()


__all__ = [
    "BlockchainProvider", "DepositInfo",
    "MockBlockchainProvider", "TronGridProvider",
    "get_blockchain_provider",
]
