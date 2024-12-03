import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
from tests.conftest import get_auth_token
from datetime import datetime


@pytest.mark.asyncio
async def test_get_user_research_history():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Получаем UUID существующего исследования
        research_uuid = await get_existing_research_uuid(ac, headers)

        response = await ac.get(f"/api/v1/desync_datas/{research_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ
        data = response.json()
        assert data["uuid"] == research_uuid  # Проверяем, что данные соответствуют запрошенному UUID


@pytest.mark.asyncio
async def test_get_research_details():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Получаем UUID существующего исследования
        research_uuid = await get_existing_research_uuid(ac, headers)

        response = await ac.get(f"/api/v1/desync_datas/{research_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ
        assert response.json()["uuid"] == research_uuid  # Проверяем, что UUID совпадает


@pytest.mark.asyncio
async def test_create_and_validate_research():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Используем реальные данные для создания нового исследования
        new_research_data = {
            "data": {},
            "device_uuid": "6442b13d-9dab-4b3c-8529-c9e9d139bb54",
            "patient_uuid": "199b998d-37a7-4420-84f7-9d6c361a7180",
            "type_research_uuid": "71cfff78-8cc9-4332-bef1-603b01d0765f",
            "user_uuid": "34f740eb-b4c7-4a63-a73c-d39a5d12488b"
        }

        # Создаем новое исследование
        response = await ac.post("/api/v1/desync_datas/registration", json=new_research_data, headers=headers, params={"duration": 30})
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешное создание
        created_research = response.json()
        assert created_research["data"] == new_research_data["data"]  # Проверяем, что данные совпадают
        assert created_research["device_uuid"] == new_research_data["device_uuid"]
        assert created_research["patient_uuid"] == new_research_data["patient_uuid"]
        assert created_research["type_research_uuid"] == new_research_data["type_research_uuid"]
        assert created_research["user_uuid"] == new_research_data["user_uuid"]


@pytest.mark.asyncio
async def test_filter_research_by_device_uuid():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Получаем токен авторизации
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        device_uuid = "6442b13d-9dab-4b3c-8529-c9e9d139bb54"
        params = {"device_uuid": device_uuid}

        # Выполняем запрос с правильными токенами и параметрами
        response = await ac.get("/api/v1/desync_datas/desync_user", headers=headers, params=params)

        # Проверяем, что ответ успешен
        assert response.status_code == status.HTTP_200_OK, f"Expected 200 but got {response.status_code}"


@pytest.mark.asyncio
async def test_filter_research_by_type_research_uuid():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Получаем токен авторизации
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        type_research_uuid = "71cfff78-8cc9-4332-bef1-603b01d0765f"
        params = {"type_research_uuid": type_research_uuid}

        # Выполняем запрос
        response = await ac.get("/api/v1/desync_datas/desync_user", headers=headers, params=params)

        # Проверяем, что ответ успешен
        assert response.status_code == status.HTTP_200_OK, f"Expected 200 but got {response.status_code}"


@pytest.mark.asyncio
async def test_filter_research_by_date_range():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Получаем токен авторизации
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        date_from = "20240901"
        date_to = "20240902"
        params = {"date_from": date_from, "date_to": date_to}

        # Выполняем запрос
        response = await ac.get("/api/v1/desync_datas/desync_user", headers=headers, params=params)

        # Проверяем, что ответ успешен
        assert response.status_code == status.HTTP_200_OK, f"Expected 200 but got {response.status_code}"


@pytest.mark.asyncio
async def test_filter_research_by_patient_uuid():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Получаем токен авторизации
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        patient_uuid = "199b998d-37a7-4420-84f7-9d6c361a7180"
        params = {"patient_uuid": patient_uuid}

        # Выполняем запрос
        response = await ac.get("/api/v1/desync_datas/desync_user", headers=headers, params=params)

        # Проверяем, что ответ успешен
        assert response.status_code == status.HTTP_200_OK, f"Expected 200 but got {response.status_code}"


@pytest.mark.asyncio
async def test_filter_research_by_partial_uuid():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Получаем токен авторизации
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        full_uuid = await get_existing_research_uuid(ac, headers)
        partial_uuid = full_uuid[:8]
        params = {"research_uuid_part": partial_uuid}
        response = await ac.get("/api/v1/desync_datas/desync_user", headers=headers, params=params)

        assert response.status_code == status.HTTP_200_OK, f"Expected 200 but got {response.status_code}"
        data = response.json()
        assert 'items' in data, "Response does not contain 'items' key"
        assert len(data['items']) > 0, "No research items found with the given partial UUID"
        for item in data['items']:
            assert partial_uuid in item['uuid'], f"UUID {item['uuid']} does not contain partial '{partial_uuid}'"


async def get_existing_research_uuid(ac, headers):
    # Запрос на получение списка исследований
    response = await ac.get("/api/v1/admin_panel/desync_datas/", headers=headers)
    assert response.status_code == status.HTTP_200_OK  # Убеждаемся, что запрос успешен
    data = response.json()
    assert 'items' in data and len(data['items']) > 0  # Проверяем, что список исследований не пустой
    return data['items'][0]['uuid']  # Возвращаем UUID первого исследования
