import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import status
from app.main import app
from tests.conftest import get_auth_token

@pytest_asyncio.fixture
async def admin_auth_headers():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac, username='test@desync.com', password='123')
    headers = {"Authorization": f"Bearer {token}"}
    return headers

# Фикстура для получения UUID первой клиники из списка
@pytest_asyncio.fixture
async def clinic_uuid(admin_auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/admin_panel/clinic/", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить список клиник: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data, list), "Ответ не является списком"
        assert len(data) > 0, "Список клиник пуст"
        return data[0]["uuid"]  # Возвращаем UUID первой клиники

@pytest.mark.asyncio
async def test_get_clinic_list(admin_auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/admin_panel/clinic/", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить список клиник: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data, list), "Ответ не является списком"
        assert len(data) > 0, "Список клиник пустой"

        # Проверяем структуру данных каждого элемента в списке
        for clinic in data:
            assert "uuid" in clinic, "Отсутствует поле 'uuid'"
            assert "name" in clinic, "Отсутствует поле 'name'"
            assert "description" in clinic, "Отсутствует поле 'description'"
            assert "logo" in clinic, "Отсутствует поле 'logo'"

@pytest.mark.asyncio
async def test_get_clinic_details(admin_auth_headers, clinic_uuid):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/admin_panel/clinic/{clinic_uuid}", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить детали клиники: {response.status_code} - {response.text}"
        data = response.json()

        # Проверяем структуру данных ответа
        assert data["uuid"] == clinic_uuid, "UUID клиники не соответствует запрошенному"
        assert "name" in data, "Отсутствует поле 'name'"
        assert "description" in data, "Отсутствует поле 'description'"
        assert "logo" in data, "Отсутствует поле 'logo'"
        assert "clinic_address" in data, "Отсутствует поле 'clinic_address'"
        assert isinstance(data["clinic_address"], list), "'clinic_address' не является списком"

        # Проверяем структуру данных для clinic_address
        for address in data["clinic_address"]:
            assert "uuid" in address, "Отсутствует поле 'uuid' в адресе клиники"
            assert "build" in address, "Отсутствует поле 'build' в адресе клиники"
            assert "phone" in address, "Отсутствует поле 'phone' в адресе клиники"
            assert "email" in address, "Отсутствует поле 'email' в адресе клиники"
            assert "clinic_uuid" in address, "Отсутствует поле 'clinic_uuid' в адресе клиники"
            assert "region" in address, "Отсутствует поле 'region' в адресе клиники"
            assert "city" in address, "Отсутствует поле 'city' в адресе клиники"
            assert "street" in address, "Отсутствует поле 'street' в адресе клиники"

@pytest.mark.asyncio
async def test_update_clinic(admin_auth_headers, clinic_uuid):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Получаем текущие данные клиники
        response = await ac.get(f"/api/v1/admin_panel/clinic/{clinic_uuid}", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить детали клиники: {response.status_code} - {response.text}"
        original_data = response.json()

        # Обновляем данные клиники
        updated_data = {
            "name": "New Clinic Name",
            "description": "Updated Description",
            "logo": "newlogo.png"
        }
        response = await ac.put(f"/api/v1/admin_panel/clinic/{clinic_uuid}", json=updated_data, headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось обновить клинику: {response.status_code} - {response.text}"
        data = response.json()

        # Проверяем, что данные обновились
        assert data["name"] == "New Clinic Name", "Поле 'name' не обновилось"
        assert data["description"] == "Updated Description", "Поле 'description' не обновилось"
        assert data["logo"] == "newlogo.png", "Поле 'logo' не обновилось"

        # Восстанавливаем оригинальные данные клиники
        response = await ac.put(f"/api/v1/admin_panel/clinic/{clinic_uuid}", json={
            "name": original_data["name"],
            "description": original_data["description"],
            "logo": original_data["logo"]
        }, headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось восстановить оригинальные данные клиники: {response.status_code} - {response.text}"
