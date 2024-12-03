import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
import uuid

from tests.conftest import get_auth_token

@pytest.mark.asyncio
async def test_get_type_research_list():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/api/v1/type_research/", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data['items'], list)
        assert len(data['items']) > 0  # Проверяем, что список не пуст

        # Дополнительная проверка структуры данных
        for item in data['items']:
            assert "name" in item
            assert "description" in item
            assert "uuid" in item

@pytest.mark.asyncio
async def test_create_type_research():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        unique_name = f"ResearchType_{uuid.uuid4()}"
        new_type_research_data = {
            "name": unique_name,
            "description": "Test Research Type"
        }
        response = await ac.post("/api/v1/type_research/registration", json=new_type_research_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["name"] == unique_name
        assert data["description"] == "Test Research Type"
        assert "uuid" in data
        return data["uuid"], unique_name

@pytest.mark.asyncio
async def test_get_type_research_details():
    type_research_uuid, unique_name = await test_create_type_research()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        response = await ac.get(f"/api/v1/type_research/{type_research_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["uuid"] == type_research_uuid
        assert data["name"] == unique_name
        assert data["description"] == "Test Research Type"

@pytest.mark.asyncio
async def test_update_type_research():
    type_research_uuid, original_name = await test_create_type_research()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        updated_name = f"{original_name}_Updated"
        updated_data = {
            "name": updated_name,
            "description": "Updated Description"
        }
        response = await ac.put(f"/api/v1/type_research/{type_research_uuid}", json=updated_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["name"] == updated_name
        assert data["description"] == "Updated Description"

        # Дополнительная проверка через GET-запрос
        response = await ac.get(f"/api/v1/type_research/{type_research_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["name"] == updated_name
        assert data["description"] == "Updated Description"

@pytest.mark.asyncio
async def test_delete_type_research():
    type_research_uuid, _ = await test_create_type_research()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        response = await ac.delete(f"/api/v1/type_research/{type_research_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        # Проверяем, что данные удалены
        response = await ac.get(f"/api/v1/type_research/{type_research_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["name"] is None
        assert data["description"] is None
        assert data["uuid"] is None

@pytest.mark.asyncio
async def test_filter_type_research_by_name():
    type_research_uuid, unique_name = await test_create_type_research()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Поиск типа исследования по имени
        response = await ac.get(f"/api/v1/type_research/", headers=headers, params={"name": unique_name})
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data['items'], list)
        assert len(data['items']) == 1  # Должен вернуться один результат

        item = data['items'][0]
        assert item["uuid"] == type_research_uuid
        assert item["name"] == unique_name
        assert item["description"] == "Test Research Type"
