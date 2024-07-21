import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config import settings
from db.db_session import create_async_session
from handlers import register_core_handlers
from middlewares import ButtonHideMiddleware, CleanerMiddleware
from middlewares.db_middleware import DbSessionMiddleware
from utils.before_bot_start import start_bot


async def _register_handlers(dp: Dispatcher) -> None:
    core_handlers_router = register_core_handlers()
    dp.include_routers(core_handlers_router)


async def _register_middlewares(
    dp: Dispatcher, async_session: async_sessionmaker[AsyncSession], bot: Bot
) -> None:
    dp.update.middleware.register(DbSessionMiddleware(async_session))
    dp.callback_query.middleware.register(ButtonHideMiddleware(bot=bot))
    dp.message.middleware.register(CleanerMiddleware(bot=bot))


async def main(bot: Bot) -> None:
    async_session: async_sessionmaker[AsyncSession] = await create_async_session(
        url=settings.asyncpg_db_url, echo=False
    )
    storage = MemoryStorage()
    dp: Dispatcher = Dispatcher(storage=storage)

    # Get commands
    await start_bot(bot)

    # Register middlewares
    await _register_middlewares(dp=dp, async_session=async_session, bot=bot)

    # Register handlers
    await _register_handlers(dp=dp)

    try:
        await dp.start_polling(bot)
    except Exception as ex:
        logging.error(ex)
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    bot_api: Bot = Bot(
        token=settings.TG_API_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    asyncio.run(main(bot_api))
