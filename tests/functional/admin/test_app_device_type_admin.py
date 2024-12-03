import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
from tests.conftest import get_auth_token
import uuid

@pytest.mark.asyncio
async def test_get_device_types_list():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/api/v1/admin_panel/devices_type/", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ
        data = response.json()
        assert isinstance(data['items'], list)  # Проверяем, что ответ является списком
        assert len(data['items']) > 0  # Проверяем, что список не пустой

        # Проверяем структуру данных типов устройств в списке
        for device_type in data['items']:
            assert "uuid" in device_type
            assert "name" in device_type
            assert "description" in device_type


@pytest.mark.asyncio
async def test_create_device_type():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Создаем новый уникальный тип устройства
        unique_name = f"DeviceType_{uuid.uuid4()}"
        new_device_type_data = {
            "name": unique_name,
            "description": "Test Device Type"
        }
        response = await ac.post("/api/v1/admin_panel/devices_type/registration", json=new_device_type_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        data = response.json()
        assert data["name"] == unique_name
        assert data["description"] == "Test Device Type"

        # Проверяем, что тип устройства появился в списке
        list_response = await ac.get("/api/v1/admin_panel/devices_type/", headers=headers)
        list_data = list_response.json()
        assert any(device_type["uuid"] == data["uuid"] for device_type in list_data["items"])

        return data["uuid"]  # Возвращаем UUID нового типа устройства


@pytest.mark.asyncio
async def test_get_device_type_details():
    device_type_uuid = await test_create_device_type()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        response = await ac.get(f"/api/v1/admin_panel/devices_type/{device_type_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        data = response.json()

        # Проверяем структуру ответа
        assert data["uuid"] == device_type_uuid
        assert "name" in data
        assert "description" in data


@pytest.mark.asyncio
async def test_update_device_type():
    device_type_uuid = await test_create_device_type()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Обновляем данные типа устройства
        updated_data = {
            "name": "Updated Device Type",
            "description": "Updated Description"
        }
        response = await ac.put(f"/api/v1/admin_panel/devices_type/{device_type_uuid}", json=updated_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        data = response.json()
        assert data["name"] == "Updated Device Type"
        assert data["description"] == "Updated Description"

        # Проверяем, что обновленный тип устройства отображается в списке с новыми данными
        list_response = await ac.get("/api/v1/admin_panel/devices_type/", headers=headers)
        list_data = list_response.json()
        assert any(device_type["uuid"] == data["uuid"] for device_type in list_data["items"])



@pytest.mark.asyncio
async def test_delete_device_type():
    device_type_uuid = await test_create_device_type()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Удаляем тип устройства
        response = await ac.delete(f"/api/v1/admin_panel/devices_type/{device_type_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        # Проверяем, что тип устройства больше не существует
        list_response = await ac.get("/api/v1/admin_panel/devices_type/", headers=headers)
        list_data = list_response.json()
        assert not any(device_type["uuid"] == device_type_uuid for device_type in list_data["items"])


@pytest.mark.asyncio
async def test_get_device_types_by_name():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Используем параметр фильтрации по имени типа устройства
        device_type_name = "AAA"
        params = {"name": device_type_name}

        response = await ac.get("/api/v1/admin_panel/devices_type/", headers=headers, params=params)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ
        data = response.json()

        assert isinstance(data['items'], list)  # Проверяем, что ответ является списком
        assert len(data['items']) > 0  # Проверяем, что список не пустой

        # Проверяем, что возвращенный тип устройства соответствует ожидаемым параметрам
        device_type_found = False
        for device_type in data['items']:
            if device_type["name"] == "AAA":
                assert device_type["description"] == "string"
                assert device_type["uuid"] == "6df6dce9-527c-4908-a104-d83d8eb5b4a9"
                device_type_found = True

        assert device_type_found, "Тип устройства с именем 'AAA' не найден в списке"