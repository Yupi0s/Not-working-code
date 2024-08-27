from dotenv import load_dotenv

import contextlib
import logging
import os
import asyncio
import time

from aiogram.types import ChatJoinRequest
from aiogram.types import Message

from aiogram import Bot, Dispatcher, F

from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

from app.database.models import async_main
from app.database.requests import update_database
from app.database.models import async_session, User

from sqlalchemy import select

load_dotenv()
token_api = os.getenv('token_api')

CHANNEL_ID = -1002216392125
ADMIN_ID = 1445020010

class Reg(StatesGroup):
    name = State()

async def requests(chat_join: ChatJoinRequest, bot: Bot):
    msg = 'Привет!👋\n\nДля того, чтобы зайти в группу, вам необходимо пройти небольшую верификацию🔐\n' \
          'Для прохождения верификации вам просто нужно ввести комманду /auth , затем ввести ваш ник из игры Clash of Clans, ' \
          'после чего вы будете приняты в группу✅'
    await bot.send_message(chat_id=chat_join.from_user.id, text=msg)

async def rules(message: Message, state: FSMContext):
    await message.answer('Ознакомление:\n\nДобро пожаловать в клан <strong>VINLAND</strong> !\n\n'
                         'Наш клан рад любым игрокам, в особенности активным и позитивным, готовым участвовать во всем и быть везде)\n\n'
                         'Основные правила клана:\n'
                         '<blockquote>1. Мат приветствуется, но в меру\n\n'
                         '2. Уважение ко всем игрокам клана\n\n'
                         '3. Активная игра(неактив более недели - кик)\n\n'
                         '4. Старейшина даётся от 260 пожертвований\n\n'
                         '5. Соруководитель даётся по доверию главы клана и/или других соруководителей\n\n'
                         '6. При вступлении в нашу группу, напишите ваш ник</blockquote>\n'
                         'Все события в клане (ИК, КВ, ЛВК, Рейды) ведутся постоянно по графику.\n\nГлава клана: @Donny_Brasko_1',
                         parse_mode='HTML')

async def cmdstart(message: Message, state: FSMContext):
    start_message = 'Привет!👋\n\nДанный бот создан с целью автоматизации принятии заявок по ссылке-приглашению :)\n\n' \
                    'Список доступных комманд:\n/auth - авторизация\n/rules - правила\n/info - информация о боте'

    await message.answer(start_message)
    await state.clear()

async def info(message: Message, state: FSMContext):
    await message.answer('<strong>Данный бот создавался специально для клана VINLAND.\n\n'
                         'По всем вопросам и предложениям, касательно бота, а также если вы нашли ошибку или баг, пишите вот сюда\n'
                         '🔑@jumbapumba     ◄-----------╯</strong>', parse_mode='HTML')

async def auth(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer('Пожалуйста, введите ваш ник...')

async def auth_step_two(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(name=message.text)
    async with async_session() as db_session:
        async with db_session.begin():
            stmt = select(User).filter(User.members == message.text)
            result = await db_session.execute(stmt)
            user = result.scalars().first()
            if user:
                await message.answer('Вы успешно авторизованы и приняты в группу!')
                await bot.approve_chat_join_request(CHANNEL_ID, message.from_user.id)
            else:
                await message.answer('Ник не найден в базе данных. Попробуйте снова.\n/auth')
            await state.clear()

async def start():
    await async_main()
    await update_database()
    print('Бот успешно включился. \nНачинаю логгирование:')
    time.sleep(0.3)
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")

    bot: Bot = Bot(token=token_api)
    dp = Dispatcher(storage=MemoryStorage())

    dp.chat_join_request.register(requests, F.chat.id == CHANNEL_ID)
    dp.message.register(cmdstart, CommandStart())
    dp.message.register(rules, Command('rules'))
    dp.message.register(info, Command('info'))
    dp.message.register(auth, Command('auth'))
    dp.message.register(auth_step_two, F.text, Reg.name)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as ex:
        logging.error(f'[Exception] - {ex}', exc_info=True)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(start())
