import logging
import asyncio
import os
import time

from aiogram import Bot, Dispatcher

from aiogram.fsm.storage.memory import MemoryStorage

from app.database.models import async_main
from app.database.requests import update_database

from app.handlers import router


async def start():
    await async_main()
    await update_database()
    print('Бот успешно включился. \nНачинаю логгирование:')
    time.sleep(0.3)
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")

    bot = Bot(token=os.getenv('token_api'))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(router)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as ex:
        logging.error(f'[Exception] - {ex}', exc_info=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
