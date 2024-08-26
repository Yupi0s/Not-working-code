from dotenv import load_dotenv
import contextlib
import asyncio
import logging
import time
import os

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

from app.database.models import async_main
from app.database.requests import update_database
from app.handlers import router

load_dotenv()
token_api = os.getenv('token_api')

bot = Bot(token=token_api)
dp = Dispatcher(storage=MemoryStorage())

async def start():
    await async_main()
    await update_database()
    dp.include_router(router)
    print('Бот успешно включен, начинаю запускать логгирование:')
    time.sleep(0.3)
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as ex:
        logging.error(f"[Exception] - {ex}", exc_info=True)
    finally:
        await bot.session.close()



if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(start())



