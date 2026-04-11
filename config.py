"""
Centralized configuration loaded from environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Telegram
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = [
        int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    ]

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Blockchain
    BLOCKCHAIN_PROVIDER: str = os.getenv("BLOCKCHAIN_PROVIDER", "mock")
    TRONGRID_API_KEY: str = os.getenv("TRONGRID_API_KEY", "")
    TRON_MASTER_ADDRESS: str = os.getenv("TRON_MASTER_ADDRESS", "")

    # Referral
    REFERRAL_COMMISSION_PCT: float = float(os.getenv("REFERRAL_COMMISSION_PCT", "10"))
    AUTO_CREDIT_REFERRAL: bool = os.getenv("AUTO_CREDIT_REFERRAL", "false").lower() == "true"

    # Worker
    DEPOSIT_CHECK_INTERVAL: int = int(os.getenv("DEPOSIT_CHECK_INTERVAL", "60"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> None:
        """Raise if critical config is missing."""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL is required")
