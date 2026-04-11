"""
Entry point – initialises database, blockchain provider, bot dispatcher,
background workers, and starts polling.
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import Config
from utils.helpers import setup_logging
from db.connection import init_db, close_db
from blockchain import get_blockchain_provider
from handlers import get_all_routers
from handlers.deposit import set_provider
from bot.middlewares import LoggingMiddleware, RateLimitMiddleware
from workers.deposit_monitor import DepositMonitor

logger = logging.getLogger(__name__)


async def main() -> None:
    # ── Setup ─────────────────────────────────────────────────────────
    Config.validate()
    setup_logging()
    logger.info("Starting bot…")

    # Database
    await init_db()

    # Blockchain provider
    provider = get_blockchain_provider()
    set_provider(provider)
    logger.info("Blockchain provider: %s", Config.BLOCKCHAIN_PROVIDER)

    # Bot & dispatcher
    bot = Bot(
        token=Config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()

    # Register middlewares (outer → applied to every update)
    dp.update.outer_middleware(LoggingMiddleware())
    dp.update.outer_middleware(RateLimitMiddleware(max_requests=10, window=5.0))

    # Register routers
    for router in get_all_routers():
        dp.include_router(router)

    # Start deposit monitor
    monitor = DepositMonitor(bot=bot, provider=provider)
    await monitor.start()

    # ── Run ───────────────────────────────────────────────────────────
    try:
        logger.info("Bot is live — polling for updates")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await monitor.stop()
        await close_db()
        await bot.session.close()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
