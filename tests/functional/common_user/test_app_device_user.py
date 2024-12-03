import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
from tests.conftest import get_auth_token


@pytest.mark.asyncio
async def test_create_device():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Проверяем, существует ли устройство с названием "MNE3"
        response = await ac.get("/api/v1/admin_panel/devices/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        devices = response.json().get('items', [])

        device_uuid = None
        for device in devices:
            if device["name"] == "MNE3":
                device_uuid = device["uuid"]
                break

        if device_uuid:
            print(f"Device 'MNE3' already exists with UUID: {device_uuid}")
        else:
            # Если устройство не найдено, создаем его
            new_device_data = {
                "name": "MNE3",
                "description": "Test Device MNE3",
                "device_types": []
            }
            response = await ac.post("/api/v1/admin_panel/devices/registration", json=new_device_data, headers=headers)
            assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

            data = response.json()
            assert data["name"] == "MNE3"
            assert data["description"] == "Test Device MNE3"
            device_uuid = data["uuid"]

        return device_uuid


@pytest.mark.asyncio
async def test_devices_list():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/api/v1/admin_panel/devices/", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ
        data = response.json()
        assert isinstance(data['items'], list)  # Проверяем, что ответ является списком
        assert len(data['items']) > 0  # Проверяем, что список не пустой

        # Найдем устройство с именем "MNE3" и вернем его UUID
        for device in data['items']:
            if device["name"] == "MNE3":
                return device["uuid"]


@pytest.mark.asyncio
async def test_device_details():
    uuid = await test_devices_list()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        response = await ac.get(f"/api/v1/admin_panel/devices/{uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        data = response.json()
        assert data["uuid"] == uuid
        assert data["name"] == "MNE3"
        assert "description" in data
        assert "clinic_uuid" in data
        assert data["status"] in [True, False]  # Проверяем, что статус имеет правильное значение


@pytest.mark.asyncio
async def test_device_on():
    uuid = await test_devices_list()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Включаем устройство
        response = await ac.put(f"/api/v1/admin_panel/devices/switch/{uuid}?status=true", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        # Проверяем, что устройство включено
        response = await ac.get(f"/api/v1/admin_panel/devices/{uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ
        data = response.json()
        assert data["status"] is True  # Убедимся, что статус устройства true (включено)


@pytest.mark.asyncio
async def test_device_calibration():
    uuid = await test_devices_list()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Калибруем устройство
        response = await ac.put(f"/api/v1/admin_panel/devices/calibration/{uuid}?calibration=true", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ


@pytest.mark.asyncio
async def test_device_off():
    uuid = await test_devices_list()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Выключаем устройство
        response = await ac.put(f"/api/v1/admin_panel/devices/switch/{uuid}?status=false", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        # Проверяем, что устройство выключено
        response = await ac.get(f"/api/v1/admin_panel/devices/{uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ
        data = response.json()
        assert data["status"] is False  # Убедимся, что статус устройства false (выключено)


@pytest.mark.asyncio
async def test_filter_devices_by_name():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        name_filter = "MNE"
        params = {"name": name_filter}

        response = await ac.get("/api/v1/admin_panel/devices/", headers=headers, params=params)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ
        data = response.json()
        assert isinstance(data['items'], list)  # Проверяем, что ответ является списком
        assert len(data['items']) > 0  # Проверяем, что список не пустой

        # Проверяем, что все устройства содержат "MNE" в названии
        for device in data['items']:
            assert name_filter in device["name"]

