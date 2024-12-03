import pytest
import time
from httpx import AsyncClient
from fastapi import status
from rethinkdb import r
from app.main import app
from tests.conftest import get_auth_token
from config.settings import settings
import uuid

def wait_for_rethinkdb(host, port, timeout=30):
    start_time = time.time()
    while True:
        try:
            conn = r.connect(host=host, port=port)
            conn.close()
            break
        except Exception as e:
            if time.time() - start_time > timeout:
                raise Exception(f"RethinkDB is not available: {e}")
            time.sleep(1)


@pytest.fixture(scope='session', autouse=True)
def ensure_rethinkdb_is_ready():
    wait_for_rethinkdb(settings.rethinkdb_host, settings.rethinkdb_port)


@pytest.mark.asyncio
async def test_get_devices_list():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/api/v1/admin_panel/devices/", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ
        data = response.json()
        assert isinstance(data['items'], list)  # Проверяем, что ответ является списком
        assert len(data['items']) > 0  # Проверяем, что список не пустой

        # Проверяем структуру данных устройств в списке
        for device in data['items']:
            assert "uuid" in device
            assert "name" in device
            assert "description" in device
            assert "clinic_uuid" in device
            assert "device_types" in device
            assert "status" in device
            assert isinstance(device["device_types"], list)


@pytest.mark.asyncio
async def test_create_device():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Создаем новое уникальное устройство
        unique_name = f"Device_{uuid.uuid4()}"
        new_device_data = {
            "name": unique_name,
            "description": "Test Device",
            "device_types": []
        }
        response = await ac.post("/api/v1/admin_panel/devices/registration", json=new_device_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        data = response.json()
        assert data["name"] == unique_name
        assert data["description"] == "Test Device"

        list_response = await ac.get("/api/v1/admin_panel/devices/", headers=headers)
        list_data = list_response.json()
        assert any(device["uuid"] == data["uuid"] for device in list_data["items"])

        return data["uuid"]


@pytest.mark.asyncio
async def test_get_device_details():
    device_uuid = await test_create_device()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        response = await ac.get(f"/api/v1/admin_panel/devices/{device_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        # Проверяем структуру ответа
        assert data["uuid"] == device_uuid
        assert "name" in data
        assert "description" in data
        assert "clinic_uuid" in data
        assert "device_types" in data
        assert isinstance(data["device_types"], list)
        assert "status" in data


@pytest.mark.asyncio
async def test_update_device():
    device_uuid = await test_create_device()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Обновляем данные устройства
        updated_data = {
            "name": "Updated Device",
            "description": "Updated Description"
        }
        response = await ac.put(f"/api/v1/admin_panel/devices/{device_uuid}", json=updated_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        data = response.json()
        assert data["name"] == "Updated Device"
        assert data["description"] == "Updated Description"

        # Проверяем, что обновленное устройство отображается в списке с новыми данными
        list_response = await ac.get("/api/v1/admin_panel/devices/", headers=headers)
        list_data = list_response.json()
        assert any(device["uuid"] == data["uuid"] for device in list_data["items"])


@pytest.mark.asyncio
async def test_device_on_off():
    device_uuid = await test_create_device()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Включаем устройство
        response = await ac.put(f"/api/v1/admin_panel/devices/switch/{device_uuid}?status=true", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        # Проверяем, что статус устройства изменился
        details_response = await ac.get(f"/api/v1/admin_panel/devices/{device_uuid}", headers=headers)
        details_data = details_response.json()
        assert details_data["status"] is True

        # Выключаем устройство
        response = await ac.put(f"/api/v1/admin_panel/devices/switch/{device_uuid}?status=false", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        # Проверяем, что статус устройства снова изменился
        details_response = await ac.get(f"/api/v1/admin_panel/devices/{device_uuid}", headers=headers)
        details_data = details_response.json()
        assert details_data["status"] is False


@pytest.mark.asyncio
async def test_device_calibration():
    device_uuid = await test_create_device()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Калибруем устройство
        response = await ac.put(f"/api/v1/admin_panel/devices/calibration/{device_uuid}?calibration=true", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ


@pytest.mark.asyncio
async def test_delete_device():
    device_uuid = await test_create_device()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Удаляем устройство
        response = await ac.delete(f"/api/v1/admin_panel/devices/{device_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        # Проверяем, что устройство больше не существует
        list_response = await ac.get("/api/v1/admin_panel/devices/", headers=headers)
        list_data = list_response.json()
        assert not any(device["uuid"] == device_uuid for device in list_data["items"])


@pytest.mark.asyncio
async def test_get_devices_by_name():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Используем параметр фильтрации по имени устройства
        device_name = "MNE3"
        params = {"name": device_name}

        response = await ac.get("/api/v1/admin_panel/devices/", headers=headers, params=params)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ
        data = response.json()

        assert isinstance(data['items'], list)  # Проверяем, что ответ является списком
        assert len(data['items']) > 0  # Проверяем, что список не пустой

        # Проверяем, что возвращенное устройство соответствует ожидаемым параметрам
        device_found = False
        for device in data['items']:
            if device["name"] == "MNE3":
                assert device["description"] == "string"
                assert device["clinic_uuid"] == "48d7663f-5bb4-4d99-ae90-bf6cc707cc3d"
                assert device["uuid"] == "6442b13d-9dab-4b3c-8529-c9e9d139bb54"
                assert isinstance(device["device_types"], list)
                assert len(device["device_types"]) == 2  # Ожидаем 2 типа устройства
                assert device["status"] is False  # Проверяем, что статус False

                # Проверяем первый тип устройства
                assert device["device_types"][0]["name"] == "AAA"
                assert device["device_types"][0]["description"] == "string"
                assert device["device_types"][0]["uuid"] == "6df6dce9-527c-4908-a104-d83d8eb5b4a9"

                # Проверяем второй тип устройства
                assert device["device_types"][1]["name"] == "BBB"
                assert device["device_types"][1]["description"] == "string"
                assert device["device_types"][1]["uuid"] == "3423201b-f79f-4cd3-9aab-dcf7495b6170"

                device_found = True

        assert device_found, "Устройство с именем 'MNE3' не найдено в списке"