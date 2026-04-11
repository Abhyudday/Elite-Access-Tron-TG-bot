"""
Aiogram middlewares – rate limiting and logging.
"""

import logging
import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Log every incoming update type and user id."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Update):
            user_id = None
            if event.message and event.message.from_user:
                user_id = event.message.from_user.id
            elif event.callback_query and event.callback_query.from_user:
                user_id = event.callback_query.from_user.id
            logger.debug("Update %s from user %s", event.update_id, user_id)
        return await handler(event, data)


class RateLimitMiddleware(BaseMiddleware):
    """
    Simple per-user rate limiter.
    Drops updates if a user sends more than `max_requests` within `window` seconds.
    """

    def __init__(self, max_requests: int = 5, window: float = 3.0) -> None:
        self._max = max_requests
        self._window = window
        self._cache: dict[int, list[float]] = {}
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id: int | None = None
        if isinstance(event, Update):
            if event.message and event.message.from_user:
                user_id = event.message.from_user.id
            elif event.callback_query and event.callback_query.from_user:
                user_id = event.callback_query.from_user.id

        if user_id is None:
            return await handler(event, data)

        now = time.monotonic()
        timestamps = self._cache.get(user_id, [])
        # Prune old timestamps
        timestamps = [t for t in timestamps if now - t < self._window]

        if len(timestamps) >= self._max:
            logger.warning("Rate-limited user %s", user_id)
            return  # Drop silently

        timestamps.append(now)
        self._cache[user_id] = timestamps
        return await handler(event, data)
