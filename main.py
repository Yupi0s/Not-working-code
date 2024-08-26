from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ChatJoinRequest
from dotenv import load_dotenv
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import os
import asyncio
import logging
import time
from sqlalchemy import select
from app.database.models import async_main, async_session, User
from app.database.requests import update_database

load_dotenv()
token_coc = os.getenv('token_coc')
token_api = os.getenv('token_api')
CLAN_TAG = os.getenv('CLAN_TAG')
CHANNEL_ID = -1002216392125
ADMIN_ID = 1445020010

class Reg(StatesGroup):
    name = State()
    check_in_db = State()

bot = Bot(token=token_api)
dp = Dispatcher()

@dp.chat_join_request()
async def chat_join_requests(bot: Bot):
    await bot.send_message('Привет!👋\n\nДля того, чтобы зайти в группу, вам необходимо пройти небольшую верификацию🔐\n'
       'Для того, чтобы пройти верификацию, вам просто нужно ввести комманду /auth , затем ввести ваш ник из игры Clash of Clans, '
       'после чего вы будете приняты в группу✅')
    await bot.send_message('Список доступных комманд:\n\n'
                           '/auth - Авторизация'
                           '/rules - правила клана'
                           '/info - информация о боте'
                           )

@dp.message(Command('auth'))
async def auth(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer('Пожалуйста, введите ваш ник...')

@dp.message(Reg.name)
async def auth_step_two(message: Message, chat_join: ChatJoinRequest, state: FSMContext):
    await state.update_data(name=message.text)
    async with async_session() as db_session:
        async with db_session.begin():
            stmt = select(User).filter(User.members == message.text)
            result = await db_session.execute(stmt)
            user = result.scalars().first()
            if user:
                await message.answer('Вы успешно авторизованы и приняты в группу!')
                await chat_join.approve()
            else:
                await message.answer('Ник не найден в базе данных. Попробуйте снова.')
                await chat_join.decline()

@dp.message(Command('rules'))
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
        'Все события в клане (ИК, КВ, ЛВК, Рейды) ведутся постоянно по графику.\n\nГлава клана: @Donny_Brasko_1', parse_mode='HTML')

@dp.message(Command('info'))
async def info(message: Message, state: FSMContext):
    await message.answer('<strong>Данный бот создавался специально для клана VINLAND.\n\n'
                         'По всем вопросам и предложениям, касательно бота, а также если вы нашли ошибку или баг, пишите вот сюда\n'
                         '🔑@jumbapumba     ◄-----------╯</strong>', parse_mode='HTML')
async def main():
    await async_main()
    await update_database()
    await dp.start_polling(bot)

if __name__ == '__main__':
    print('Бот успешно включен, начинаю запускать логгирование:')
    time.sleep(0.3)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
    )
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nБот выключен. До встречи!")


