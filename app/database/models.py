#База данных
from sqlalchemy import TEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.VINLAND')

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'players'

    id: Mapped[str] = mapped_column(primary_key=True, type_=TEXT, nullable=True)
    members: Mapped[str] = mapped_column(unique=True, type_=TEXT, nullable=True)
    TownHall_lvl: Mapped[int] = mapped_column(nullable=True)
    trophies: Mapped[int] = mapped_column(nullable=True)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)