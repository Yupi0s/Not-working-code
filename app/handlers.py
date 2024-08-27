#Хэндлеры
from aiogram.client import bot
from dotenv import load_dotenv
import os

from aiogram.types import Message
from aiogram.types.chat_join_request import ChatJoinRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import StatesGroup, State

from aiogram import Bot, F, Router

from aiogram.fsm.context import FSMContext
from app.database.models import async_session, User
from sqlalchemy import select

router = Router()
load_dotenv()
token_api = os.getenv('token_api')
CHANNEL_ID = os.getenv('CHANNEL_ID')
bot = Bot(token=token_api)

class Reg(StatesGroup):
    name = State()

@router.chat_join_request(F.chat.id == CHANNEL_ID)
async def chat_join_requests(chat_join: ChatJoinRequest):
    msg = 'Привет!👋\n\nДля того, чтобы зайти в группу, вам необходимо пройти небольшую верификацию🔐\n' \
          'Для прохождения верификации вам просто нужно ввести комманду /auth , затем ввести ваш ник из игры Clash of Clans, ' \
          'после чего вы будете приняты в группу✅'

    msg2 = 'Список доступных комманд:\n\n' \
           '/auth - Авторизация\n/rules - правила клана\n/info - информация о боте'

    await bot.send_message(chat_id=chat_join.user_chat_id, text=msg) #Отправка сообщения не срабатывает!!!
    await bot.send_message(chat_id=chat_join.user_chat_id, text=msg2) #Отправка сообщения не срабатывает!!!

@router.message(CommandStart())
async def auth(message: Message, state: FSMContext):
    start_message = 'Привет!👋\n\nДанный бот создан с целью автоматизации принятии заявок по ссылке-приглашению :)\n\n' \
                    'Список доступных комманд:\n/auth - авторизация\n/rules - правила\n/info - информация о боте'

    await message.answer(start_message)
    await state.clear()

@router.message(Command('rules'))
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

@router.message(Command('info'))
async def info(message: Message, state: FSMContext):
    await message.answer('<strong>Данный бот создавался специально для клана VINLAND.\n\n'
                         'По всем вопросам и предложениям, касательно бота, а также если вы нашли ошибку или баг, пишите вот сюда\n'
                         '🔑@jumbapumba     ◄-----------╯</strong>', parse_mode='HTML')

@router.message(Command('auth'))
async def auth(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer('Пожалуйста, введите ваш ник...')

@router.message(F.text, Reg.name)
async def auth_step_two(message: Message, state: FSMContext):
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

