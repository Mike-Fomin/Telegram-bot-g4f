import asyncio
import logging
import redis

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from config_data.config import load_config, Config
from handlers.command_handlers import command_router
from handlers.user_handlers import user_router
from middlewares.outer_middleware import AdminListMiddleware

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, admins: list[int]):
    for admin in admins:
        await bot.send_message(
            chat_id=admin,
            text='Бот запущен'
        )


async def main() -> None:

    logging.basicConfig(
        level=logging.INFO,
        style='{',
        format='{filename}:{lineno} #{levelname:8} [{asctime}] - {name} - {message}'
    )
    logger.info('Starting bot')

    config: Config = load_config()

    try:
        storage = RedisStorage.from_url("redis://localhost:6379")
        logging.debug(await storage.redis.ping())
    except redis.exceptions.ConnectionError:
        storage = MemoryStorage()
        logging.debug("Подключено хранилище MemoryStorage")
    else:
        logging.debug("Подключено хранилище Redis")

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)

    dp.workflow_data.update({'admins': config.tg_bot.admin_ids})
    dp.workflow_data.update({'send_chat_id': config.tg_bot.chat_id})
    dp.update.middleware(AdminListMiddleware())

    dp.include_router(command_router)
    dp.include_router(user_router)

    await on_startup(bot, config.tg_bot.admin_ids)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

