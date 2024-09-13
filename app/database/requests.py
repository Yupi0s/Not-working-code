from app.database.models import async_session
from app.database.models import User

from sqlalchemy import select, delete

from dotenv import load_dotenv

import os
import aiohttp

load_dotenv()
CLAN_TAG = os.getenv('CLAN_TAG')
API_COC = os.getenv('token_coc')


# Подключение к API Clash Of Clans
async def fetch_clan_members(session):
    url = f'https://api.clashofclans.com/v1/clans/{CLAN_TAG.replace("#", "%23")}/members'
    headers = {
        'Authorization': f'Bearer {API_COC}'
    }
    async with session.get(url, headers=headers) as response:
        return await response.json()


async def update_database():
    async with aiohttp.ClientSession() as session:
        print('База данных обновлена')
        data = await fetch_clan_members(session)
        members = data.get('items', [])

        async with async_session() as db_session:
            async with db_session.begin():
                # Очистка старых данных
                await db_session.execute(delete(User))

                # Добавление новых данных
                for member in members:
                    existing_user = await db_session.execute(select(User).filter_by(members=member['name']))
                    existing_user = existing_user.scalars().first()

                    if not existing_user:
                        new_user = User(
                            id=member['tag'],
                            members=member['name'],
                            TownHall_lvl=member['townHallLevel'],
                            trophies=member['trophies']
                        )
                        db_session.add(new_user)
