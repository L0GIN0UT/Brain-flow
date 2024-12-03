import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import status
from app.main import app
from tests.conftest import get_auth_token


@pytest_asyncio.fixture
async def auth_headers():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
    headers = {"Authorization": f"Bearer {token}"}
    return headers


@pytest_asyncio.fixture
async def clinic_address_uuid(auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/admin_panel/clinic_address/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить список адресов клиник: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Ответ не является списком"
        assert len(data) > 0, "Список адресов клиник пуст"
        return data[0]["uuid"]


@pytest.mark.asyncio
async def test_get_clinic_address_list(auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/admin_panel/clinic_address/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить список адресов клиник: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Ответ не является списком"
        assert len(data) > 0, "Список адресов клиник пуст"

        # Проверяем структуру данных каждого элемента в списке
        for item in data:
            assert "uuid" in item, "Отсутствует поле 'uuid'"
            assert "build" in item, "Отсутствует поле 'build'"
            assert "phone" in item, "Отсутствует поле 'phone'"
            assert "email" in item, "Отсутствует поле 'email'"
            assert "clinic_uuid" in item, "Отсутствует поле 'clinic_uuid'"
            assert "region" in item, "Отсутствует поле 'region'"
            assert "city" in item, "Отсутствует поле 'city'"
            assert "street" in item, "Отсутствует поле 'street'"


@pytest.mark.asyncio
async def test_get_clinic_address_details(auth_headers, clinic_address_uuid):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/admin_panel/clinic_address/{clinic_address_uuid}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить детали адреса клиники: {response.text}"
        data = response.json()

        # Проверяем структуру данных ответа
        assert data["uuid"] == clinic_address_uuid, "UUID адреса клиники не соответствует запрошенному"
        assert "build" in data, "Отсутствует поле 'build'"
        assert "phone" in data, "Отсутствует поле 'phone'"
        assert "email" in data, "Отсутствует поле 'email'"
        assert "clinic_uuid" in data, "Отсутствует поле 'clinic_uuid'"
        assert "region" in data, "Отсутствует поле 'region'"
        assert "city" in data, "Отсутствует поле 'city'"
        assert "street" in data, "Отсутствует поле 'street'"


@pytest.mark.asyncio
async def test_update_clinic_address(auth_headers, clinic_address_uuid):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Сохраняем текущие данные адреса клиники
        response = await ac.get(f"/api/v1/admin_panel/clinic_address/{clinic_address_uuid}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить детали адреса клиники: {response.text}"
        original_data = response.json()

        # Выполняем обновление данных адреса клиники
        updated_data = {
            "region": "Updated Region",
            "city": "Updated City",
            "street": "Updated Street",
            "build": "New Building",
            "phone": "+9876543210",
            "email": "newemail@example.com"
        }
        response = await ac.put(f"/api/v1/admin_panel/clinic_address/{clinic_address_uuid}", json=updated_data,
                                headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось обновить адрес клиники: {response.text}"

        # Проверяем, что обновление прошло успешно
        data = response.json()
        assert data["region"] == "Updated Region", "Поле 'region' не обновилось"
        assert data["city"] == "Updated City", "Поле 'city' не обновилось"
        assert data["street"] == "Updated Street", "Поле 'street' не обновилось"
        assert data["build"] == "New Building", "Поле 'build' не обновилось"
        assert data["phone"] == "+9876543210", "Поле 'phone' не обновилось"
        assert data["email"] == "newemail@example.com", "Поле 'email' не обновилось"

        # Восстанавливаем оригинальные данные адреса клиники
        response = await ac.put(f"/api/v1/admin_panel/clinic_address/{clinic_address_uuid}", json=original_data,
                                headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось восстановить оригинальные данные: {response.text}"
