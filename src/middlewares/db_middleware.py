import logging
from typing import Any
from collections.abc import Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

_logger = logging.getLogger(__name__)


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker[AsyncSession]) -> None:
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Awaitable[Any]:
        _logger.debug(f"Acquiring DB session from pool for {event.update_id}")
        async with self.session_pool() as session:
            data["db_session"] = session
            return await handler(event, data)
