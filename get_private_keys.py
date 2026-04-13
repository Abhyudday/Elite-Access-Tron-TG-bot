"""
One-off script to derive deposit wallet private keys for given users
AND compare with what is stored in the database.
Usage: python3 get_private_keys.py
"""

import asyncio
import hmac
import hashlib
from dotenv import load_dotenv
from config import Config
from tronpy.keys import PrivateKey

load_dotenv()

USERS = [1426081243, 7727271010]

master_key = "cda71055c0863b72ecb65c07f0e38d3694a819f9a95b8a776de33c897b458d34"
master_key_bytes = master_key.encode()


async def main():
    from db.connection import init_db, get_session
    from db.models import Deposit
    from sqlalchemy import select

    await init_db()

    async with get_session() as session:
        for uid in USERS:
            # Derive address from master key
            derived = hmac.new(master_key_bytes, str(uid).encode(), hashlib.sha256).digest()
            priv = PrivateKey(private_key_bytes=derived)
            derived_addr = priv.public_key.to_base58check_address()

            # Query DB for stored address
            result = await session.execute(
                select(Deposit).where(Deposit.user_telegram_id == uid)
            )
            deposit = result.scalar_one_or_none()
            db_addr = deposit.address if deposit else "NOT FOUND"

            match = "✅ MATCH" if derived_addr == db_addr else "❌ MISMATCH"

            print(f"User:           {uid}")
            print(f"DB Address:     {db_addr}")
            print(f"Derived Address:{derived_addr}")
            print(f"Status:         {match}")
            print(f"Private Key:    {priv.hex()}")
            print("-" * 60)


asyncio.run(main())
