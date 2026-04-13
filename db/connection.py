"""
Async SQLAlchemy engine and session factory for PostgreSQL.
"""

import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import Config

logger = logging.getLogger(__name__)

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_db() -> None:
    """Create the engine and session factory; create tables if needed."""
    global _engine, _session_factory

    url = Config.DATABASE_URL
    # Railway sometimes provides postgres:// which asyncpg needs as postgresql+asyncpg://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    _engine = create_async_engine(url, echo=False, pool_size=10, max_overflow=20)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)

    # Auto-create tables
    from db.models import Base
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Migrate: add new columns to existing tables if they don't exist
    async with _engine.begin() as conn:
        from sqlalchemy import text
        migrations = [
            ("users", "payout_address", "VARCHAR(64)"),
            ("users", "language", "VARCHAR(2) DEFAULT 'en' NOT NULL"),
            ("commissions", "commission_pct", "DOUBLE PRECISION DEFAULT 0 NOT NULL"),
            ("commissions", "payout_tx_hash", "VARCHAR(128)"),
        ]
        for table, col, col_def in migrations:
            try:
                await conn.execute(text(
                    f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {col_def}"
                ))
            except Exception:
                pass

    logger.info("Database initialised")


async def close_db() -> None:
    """Dispose the engine pool."""
    global _engine
    if _engine:
        await _engine.dispose()
        logger.info("Database connection closed")


def get_session() -> AsyncSession:
    """Return a new async session. Caller must use `async with`."""
    if _session_factory is None:
        raise RuntimeError("Database not initialised – call init_db() first")
    return _session_factory()
