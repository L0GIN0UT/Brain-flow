import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
from tests.conftest import get_auth_token
import uuid


@pytest.mark.asyncio
async def test_get_type_research_list():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/api/v1/admin_panel/type_research/", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ
        data = response.json()

        # Проверяем общую структуру ответа
        assert isinstance(data['items'], list)
        assert data["total"] > 0
        assert data["page"] == 1
        assert data["size"] > 0
        assert data["pages"] >= 1

        # Проверяем каждый элемент в списке
        for item in data['items']:
            assert "uuid" in item and isinstance(item["uuid"], str)
            assert "name" in item and isinstance(item["name"], str)
            assert "description" in item and isinstance(item["description"], str)


@pytest.mark.asyncio
async def test_create_type_research():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Создаем новый уникальный тип исследования
        unique_name = f"ResearchType_{uuid.uuid4()}"
        new_type_research_data = {
            "name": unique_name,
            "description": "Test Research Type"
        }
        response = await ac.post("/api/v1/admin_panel/type_research/registration", json=new_type_research_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        data = response.json()
        assert data["name"] == unique_name
        assert data["description"] == "Test Research Type"

        # Проверяем, что тип исследования был добавлен в список
        type_research_uuid = data["uuid"]
        list_response = await ac.get("/api/v1/admin_panel/type_research/", headers=headers)
        list_data = list_response.json()
        assert any(item["uuid"] == type_research_uuid for item in list_data["items"])

        return type_research_uuid  # Возвращаем UUID нового типа исследования


@pytest.mark.asyncio
async def test_get_type_research_details():
    type_research_uuid = await test_create_type_research()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        response = await ac.get(f"/api/v1/admin_panel/type_research/{type_research_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Проверяем структуру и значения ответа
        assert data["uuid"] == type_research_uuid
        assert "name" in data and isinstance(data["name"], str)
        assert "description" in data and isinstance(data["description"], str)


@pytest.mark.asyncio
async def test_update_type_research():
    type_research_uuid = await test_create_type_research()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Обновляем данные типа исследования
        updated_data = {
            "name": "Updated Research Type",
            "description": "Updated Description"
        }
        response = await ac.put(f"/api/v1/admin_panel/type_research/{type_research_uuid}", json=updated_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        # Проверяем, что данные обновились
        updated_response = await ac.get(f"/api/v1/admin_panel/type_research/{type_research_uuid}", headers=headers)
        updated_data_response = updated_response.json()

        assert updated_data_response["name"] == "Updated Research Type"
        assert updated_data_response["description"] == "Updated Description"


@pytest.mark.asyncio
async def test_delete_type_research():
    type_research_uuid = await test_create_type_research()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Удаляем тип исследования
        response = await ac.delete(f"/api/v1/admin_panel/type_research/{type_research_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        # Проверяем, что данные типа исследования очищены
        check_response = await ac.get(f"/api/v1/admin_panel/type_research/{type_research_uuid}", headers=headers)
        assert check_response.status_code == status.HTTP_200_OK
        data = check_response.json()
        assert data["name"] is None
        assert data["description"] is None
        assert data["uuid"] is None


@pytest.mark.asyncio
async def test_filter_type_research_by_name():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        name_filter = "Updated Research Type"
        params = {"name": name_filter}

        response = await ac.get("/api/v1/admin_panel/type_research/", headers=headers, params=params)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Проверяем, что отфильтрованный список содержит элементы с заданным именем
        assert isinstance(data['items'], list)
        assert len(data['items']) > 0

        for item in data['items']:
            assert name_filter in item["name"]

