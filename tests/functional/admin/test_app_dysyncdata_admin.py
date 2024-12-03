import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import status
from datetime import datetime, timezone
from app.main import app
from tests.conftest import get_auth_token


# Фикстура для получения заголовков аутентификации администратора
@pytest_asyncio.fixture
async def admin_auth_headers():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac, username='test@desync.com', password='123')
    headers = {"Authorization": f"Bearer {token}"}
    return headers

# Фикстура для получения UUID первого desync data
@pytest_asyncio.fixture
async def desync_uuid(admin_auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/admin_panel/desync_datas/", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить список desync data: {response.status_code} - {response.text}"
        data = response.json()
        assert data['items'], "Список desync data пуст"
        return data['items'][0]['uuid']  # Возвращаем UUID первого исследования


@pytest.mark.asyncio
async def test_get_desync_datas_list(admin_auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/admin_panel/desync_datas/", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить список desync data: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data['items'], list), "Ответ не является списком"
        assert len(data['items']) > 0, "Список desync data пуст"


@pytest.mark.asyncio
async def test_get_desync_details(admin_auth_headers, desync_uuid):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/admin_panel/desync_datas/{desync_uuid}", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить детали desync data: {response.status_code} - {response.text}"

        data = response.json()

        # Проверяем структуру ответа
        assert data["uuid"] == desync_uuid
        assert "date" in data
        assert "device_uuid" in data
        assert "patient_uuid" in data
        assert "type_research_uuid" in data
        assert "user_uuid" in data
        assert "data" in data


@pytest.mark.asyncio
async def test_update_desync_data(admin_auth_headers, desync_uuid):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Выполняем обновление данных исследования
        updated_data = {
            "data": {"key": "new_value"},
            "date": "2024-01-01T00:00:00Z"
        }
        response = await ac.put(f"/api/v1/admin_panel/desync_datas/{desync_uuid}", json=updated_data, headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось обновить desync data: {response.status_code} - {response.text}"

        # Проверяем, что обновление прошло успешно
        data = response.json()
        assert data["data"] == {"key": "new_value"}
        # Приводим формат даты к общему виду
        assert data["date"][:19] == "2024-01-01T00:00:00"


@pytest.mark.asyncio
async def test_delete_desync_data(admin_auth_headers, desync_uuid):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Выполняем удаление данных исследования
        response = await ac.delete(f"/api/v1/admin_panel/desync_datas/{desync_uuid}", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось удалить desync data: {response.status_code} - {response.text}"

        # Проверяем, что данные исследования были "очищены"
        check_response = await ac.get(f"/api/v1/admin_panel/desync_datas/{desync_uuid}", headers=admin_auth_headers)
        assert check_response.status_code == status.HTTP_200_OK, f"Не удалось получить детали desync data после удаления: {check_response.status_code} - {check_response.text}"
        data = check_response.json()
        assert data["data"] == {}
        assert data["date"] is None
        assert data["device_uuid"] is None
        assert data["patient_uuid"] is None
        assert data["type_research_uuid"] is None
        assert data["user_uuid"] is None
        assert data["uuid"] is None


@pytest.mark.asyncio
async def test_filter_desync_datas_by_user_uuid(admin_auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        user_uuid = "fb91ae14-5ad5-4498-b6c2-a89aaf03bd3f"
        params = {"user_uuid": user_uuid}

        response = await ac.get("/api/v1/admin_panel/desync_datas/", headers=admin_auth_headers, params=params)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить desync data по user_uuid: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data['items'], list), "Ответ не является списком"
        assert len(data['items']) > 0, "Список desync data пуст"

        for item in data['items']:
            assert item["user_uuid"] == user_uuid


@pytest.mark.asyncio
async def test_filter_desync_datas_by_device_uuid(admin_auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        device_uuid = "6442b13d-9dab-4b3c-8529-c9e9d139bb54"
        params = {"device_uuid": device_uuid}

        response = await ac.get("/api/v1/admin_panel/desync_datas/", headers=admin_auth_headers, params=params)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить desync data по device_uuid: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data['items'], list), "Ответ не является списком"
        assert len(data['items']) > 0, "Список desync data пуст"

        for item in data['items']:
            assert item["device_uuid"] == device_uuid


@pytest.mark.asyncio
async def test_filter_desync_datas_by_type_research_uuid(admin_auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        type_research_uuid = "71cfff78-8cc9-4332-bef1-603b01d0765f"
        params = {"type_research_uuid": type_research_uuid}

        response = await ac.get("/api/v1/admin_panel/desync_datas/", headers=admin_auth_headers, params=params)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить desync data по type_research_uuid: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data['items'], list), "Ответ не является списком"
        assert len(data['items']) > 0, "Список desync data пуст"

        for item in data['items']:
            assert item["type_research_uuid"] == type_research_uuid


@pytest.mark.asyncio
async def test_filter_desync_datas_by_patient_uuid(admin_auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        patient_uuid = "199b998d-37a7-4420-84f7-9d6c361a7180"
        params = {"patient_uuid": patient_uuid}

        response = await ac.get("/api/v1/admin_panel/desync_datas/", headers=admin_auth_headers, params=params)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить desync data по patient_uuid: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data['items'], list), "Ответ не является списком"
        assert len(data['items']) > 0, "Список desync data пуст"

        for item in data['items']:
            assert item["patient_uuid"] == patient_uuid


@pytest.mark.asyncio
async def test_filter_desync_datas_by_date_range(admin_auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        date_from = "20240101"
        date_to = "20241231"
        params = {"date_from": date_from, "date_to": date_to}

        response = await ac.get("/api/v1/admin_panel/desync_datas/", headers=admin_auth_headers, params=params)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить desync data по диапазону дат: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data['items'], list), "Ответ не является списком"
        assert len(data['items']) > 0, "Список desync data пуст"

        date_from_dt = datetime.strptime(date_from, "%Y%m%d").replace(tzinfo=timezone.utc)
        date_to_dt = datetime.strptime(date_to, "%Y%m%d").replace(tzinfo=timezone.utc)

        for item in data['items']:
            if item["date"]:
                try:
                    item_date = datetime.fromisoformat(item["date"])
                    if item_date.tzinfo is None:
                        item_date = item_date.replace(tzinfo=timezone.utc)
                    assert date_from_dt <= item_date <= date_to_dt, f"Дата {item_date} вне диапазона {date_from_dt} - {date_to_dt}"
                except ValueError as e:
                    print(f"Ошибка разбора даты: {e}. Строка с датой: {item['date']}")


@pytest.mark.asyncio
async def test_filter_desync_datas_by_research_uuid_part(admin_auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Шаг 1: Получаем список исследований
        response = await ac.get("/api/v1/admin_panel/desync_datas/", headers=admin_auth_headers)
        assert response.status_code == status.HTTP_200_OK, f"Не удалось получить список desync data: {response.status_code} - {response.text}"

        data = response.json()
        assert len(data['items']) > 0, "Список desync data пуст"

        # Берем UUID первого исследования
        full_uuid = data['items'][0]['uuid']
        assert full_uuid, "UUID исследования не найден"

        # Шаг 2: Используем часть UUID для фильтрации
        research_uuid_part = full_uuid[:8]  # Используем первые 8 символов UUID

        params = {"research_uuid_part": research_uuid_part}
        search_response = await ac.get("/api/v1/admin_panel/desync_datas/", headers=admin_auth_headers, params=params)
        assert search_response.status_code == status.HTTP_200_OK, f"Не удалось выполнить поиск по части UUID: {search_response.status_code} - {search_response.text}"

        search_data = search_response.json()
        assert isinstance(search_data['items'], list), "Ответ поиска не является списком"
        assert len(search_data['items']) > 0, "Поиск по части UUID не дал результатов"

        # Шаг 3: Проверяем, что найденное исследование содержит нужную часть UUID
        for item in search_data['items']:
            assert research_uuid_part in item[
                'uuid'], f"Часть UUID '{research_uuid_part}' не найдена в полном UUID '{item['uuid']}'"