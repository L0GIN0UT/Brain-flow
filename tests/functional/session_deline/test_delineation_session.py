import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app

@pytest.mark.asyncio
async def test_session_delineation():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Данные пользователя
        login_data = {
            "username": "test@desync.com",
            "password": "123"
        }

        # Логинимся с устройства 1
        response = await client.post("/api/v1/login/authorization", data=login_data)
        if response.status_code != status.HTTP_200_OK:
            print("Ошибка при авторизации устройства 1:")
            print(response.status_code)
            print(response.text)
        assert response.status_code == status.HTTP_200_OK, f"Авторизация не удалась для устройства 1: {response.text}"
        token1 = response.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        print(f"Token1: {token1}")

        # Проверяем, что устройство 1 может получить доступ к списку клиник
        response = await client.get("/api/v1/admin_panel/clinic/", headers=headers1)
        assert response.status_code == status.HTTP_200_OK, "Ожидался успешный доступ для устройства 1"

        # Логинимся с устройства 2 (та же учетная запись)
        response = await client.post("/api/v1/login/authorization", data=login_data)
        assert response.status_code == status.HTTP_200_OK, f"Авторизация не удалась для устройства 2: {response.text}"
        token2 = response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        print(f"Token2: {token2}")

        # Проверяем, что устройство 1 теперь должно быть разлогинено
        response = await client.get("/api/v1/admin_panel/clinic/", headers=headers1)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, "Ожидалось, что устройство 1 будет отключено"

        # Проверяем, что устройство 2 может получить доступ
        response = await client.get("/api/v1/admin_panel/clinic/", headers=headers2)
        assert response.status_code == status.HTTP_200_OK, "Ожидался успешный доступ для устройства 2"

        # Логинимся с устройства 3 (та же учетная запись)
        response = await client.post("/api/v1/login/authorization", data=login_data)
        assert response.status_code == status.HTTP_200_OK, f"Авторизация не удалась для устройства 3: {response.text}"
        token3 = response.json()["access_token"]
        headers3 = {"Authorization": f"Bearer {token3}"}
        print(f"Token3: {token3}")

        # Проверяем, что устройство 2 теперь должно быть разлогинено
        response = await client.get("/api/v1/admin_panel/clinic/", headers=headers2)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, "Ожидалось, что устройство 2 будет отключено"

        # Проверяем, что устройство 3 может получить доступ
        response = await client.get("/api/v1/admin_panel/clinic/", headers=headers3)
        assert response.status_code == status.HTTP_200_OK, "Ожидался успешный доступ для устройства 3"
