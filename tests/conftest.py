import asyncio
import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.postgres import metadata, get_session
from app.main import app

# Установка URI для тестовой базы данных
DATABASE_URI = f'postgresql+asyncpg://postgres:postgres@pg_db:5432/desyncDB'

# Создание движка и сессии для тестирования
engine_test = create_async_engine(DATABASE_URI, echo=True, future=True)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
metadata.bind = engine_test

# Переопределение сессии для тестирования
async def override_get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

# Переопределение зависимости в приложении
app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    # Если нужно сбросить базу данных после тестов, разкомментируйте:
    # async with engine_test.begin() as conn:
    #     await conn.run_sync(metadata.drop_all)

# Фикстура для создания нового цикла событий
@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Обновленная функция get_auth_token
async def get_auth_token(client: AsyncClient, username: str = "test@desync.com", password: str = "123") -> str:
    """Функция для получения токена авторизации."""
    response = await client.post("/api/v1/login/authorization", data={"username": username, "password": password})
    assert response.status_code == status.HTTP_200_OK, f"Не удалось получить токен: {response.status_code} - {response.text}"
    return response.json()["access_token"]
