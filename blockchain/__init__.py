from blockchain.base import BlockchainProvider, DepositInfo
from blockchain.mock_provider import MockBlockchainProvider
from blockchain.trongrid_provider import TronGridProvider
from config import Config


def get_blockchain_provider() -> BlockchainProvider:
    """Factory: return the configured blockchain provider."""
    if Config.BLOCKCHAIN_PROVIDER == "trongrid":
        master_key = Config.TRON_MASTER_KEY or Config.TRONGRID_API_KEY
        if not master_key:
            raise ValueError("Either TRON_MASTER_KEY or TRONGRID_API_KEY must be set when BLOCKCHAIN_PROVIDER=trongrid")
        return TronGridProvider(api_key=Config.TRONGRID_API_KEY, master_key=master_key)
    return MockBlockchainProvider()


__all__ = [
    "BlockchainProvider", "DepositInfo",
    "MockBlockchainProvider", "TronGridProvider",
    "get_blockchain_provider",
]
