# db/postgres.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from sqlmodel import SQLModel

from config.settings import settings

user = settings.postgres_user
password = settings.postgres_password
host = settings.postgres_host
port = settings.postgres_port
db_name = settings.postgres_db

# DATABASE_URI = 'postgresql+asyncpg://postgres:postgres@localhost:5432/desyncDB'
DATABASE_URI = f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}'
Base = declarative_base()

metadata = MetaData()

engine = create_async_engine(DATABASE_URI, echo=True, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


