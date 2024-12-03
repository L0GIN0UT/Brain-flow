import pytest
from httpx import AsyncClient
from fastapi import status
from uuid import uuid4
from app.main import app
from tests.conftest import get_auth_token


@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        unique_phone = f"+123456789{str(uuid4().int)[:6]}"
        unique_email = f"user.{uuid4().hex[:8]}@mail.ru"
        unique_avatar = f"avatar_{uuid4().hex[:8]}"
        new_user_data = {
            "password": "password123",
            "last_name": "Doe",
            "first_name": "John",
            "patronymic": "Jr.",
            "phone": unique_phone,
            "email": unique_email,
            "avatar": unique_avatar,
            "profession": "Doctor"
        }
        response = await ac.post("/api/v1/admin_panel/user/registration/", json=new_user_data, headers=headers)

        # Проверка на перенаправление
        if response.status_code == status.HTTP_307_TEMPORARY_REDIRECT:
            response = await ac.post(response.headers['Location'], json=new_user_data, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Проверка, что пользователь был успешно создан с правильными данными
        assert data["email"] == unique_email
        assert data["phone"] == unique_phone
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["patronymic"] == "Jr."
        assert data["avatar"] == unique_avatar
        assert data["profession"] == "Doctor"

        return data["uuid"], unique_phone, unique_email


@pytest.mark.asyncio
async def test_get_user_list():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/api/v1/admin_panel/user", headers=headers)

        # Проверка на перенаправление
        if response.status_code == status.HTTP_307_TEMPORARY_REDIRECT:
            response = await ac.get(response.headers['Location'], headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Проверка структуры ответа
        assert isinstance(data['items'], list)
        assert data["total"] > 0
        assert data["page"] == 1
        assert data["size"] > 0
        assert data["pages"] >= 1

        # Проверка каждого элемента в списке
        for item in data['items']:
            assert "uuid" in item and isinstance(item["uuid"], str)
            assert "last_name" in item and isinstance(item["last_name"], str)
            assert "first_name" in item and isinstance(item["first_name"], str)
            assert "patronymic" in item and (item["patronymic"] is None or isinstance(item["patronymic"], str))
            assert "phone" in item and isinstance(item["phone"], str)
            assert "email" in item and isinstance(item["email"], str)
            assert "avatar" in item and (item["avatar"] is None or isinstance(item["avatar"], str))
            assert "profession" in item and (item["profession"] is None or isinstance(item["profession"], str))


@pytest.mark.asyncio
async def test_get_user_details():
    user_uuid, _, _ = await test_create_user()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get(f"/api/v1/admin_panel/user/{user_uuid}", headers=headers)

        # Проверка на перенаправление
        if response.status_code == status.HTTP_307_TEMPORARY_REDIRECT:
            response = await ac.get(response.headers['Location'], headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Проверка деталей пользователя
        assert data["uuid"] == user_uuid
        assert "last_name" in data and isinstance(data["last_name"], str)
        assert "first_name" in data and isinstance(data["first_name"], str)
        assert "patronymic" in data and (data["patronymic"] is None or isinstance(data["patronymic"], str))
        assert "phone" in data and isinstance(data["phone"], str)
        assert "email" in data and isinstance(data["email"], str)
        assert "avatar" in data and (data["avatar"] is None or isinstance(data["avatar"], str))
        assert "profession" in data and (data["profession"] is None or isinstance(data["profession"], str))


@pytest.mark.asyncio
async def test_update_user():
    user_uuid, phone, _ = await test_create_user()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        updated_data = {
            "phone": phone,
            "first_name": "Jane"
        }
        response = await ac.put(f"/api/v1/admin_panel/user/{user_uuid}", json=updated_data, headers=headers)

        # Проверка на перенаправление
        if response.status_code == status.HTTP_307_TEMPORARY_REDIRECT:
            response = await ac.put(response.headers['Location'], json=updated_data, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Проверка, что данные обновлены
        assert data["uuid"] == user_uuid
        assert data["first_name"] == "Jane"
        assert data["phone"] == phone


@pytest.mark.asyncio
async def test_delete_user():
    user_uuid, _, _ = await test_create_user()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.delete(f"/api/v1/admin_panel/user/{user_uuid}", headers=headers)

        # Проверка на перенаправление
        if response.status_code == status.HTTP_307_TEMPORARY_REDIRECT:
            response = await ac.delete(response.headers['Location'], headers=headers)

        assert response.status_code == status.HTTP_200_OK

        # Проверка, что пользователь удален
        check_response = await ac.get(f"/api/v1/admin_panel/user/{user_uuid}", headers=headers)
        assert check_response.status_code == status.HTTP_200_OK
        data = check_response.json()
        assert data["uuid"] is None
        assert data["last_name"] is None
        assert data["first_name"] is None
        assert data["patronymic"] is None
        assert data["phone"] is None
        assert data["email"] is None
        assert data["avatar"] is None
        assert data["profession"] is None


@pytest.mark.asyncio
async def test_create_user_with_specific_email():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        unique_avatar = f"avatar_{uuid4().hex[:8]}"
        new_user_data = {
            "password": "password123",
            "last_name": "Doe",
            "first_name": "John",
            "patronymic": "Jr.",
            "phone": f"+123456789{str(uuid4().int)[:6]}",
            "email": "ivan.login.02@mail.ru",
            "avatar": unique_avatar,
            "profession": "Doctor"
        }

        response = await ac.post("/api/v1/admin_panel/user/registration/", json=new_user_data, headers=headers)

        # Проверка на перенаправление
        if response.status_code == status.HTTP_307_TEMPORARY_REDIRECT:
            response = await ac.post(response.headers['Location'], json=new_user_data, headers=headers)

        if response.status_code != status.HTTP_200_OK:
            if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                response = await ac.get("/api/v1/admin_panel/user/", headers=headers,
                                        params={"email": "ivan.login.02@mail.ru"})
                assert response.status_code == status.HTTP_200_OK
                data = response.json()

                # Ищем пользователя в списке `items`
                user = next((item for item in data["items"] if item["email"] == "ivan.login.02@mail.ru"), None)
                assert user is not None, "User not found in response data"
                return user["uuid"], user["phone"]
        else:
            data = response.json()
            return data["uuid"], data["phone"]


@pytest.mark.asyncio
async def test_recovery_password():
    await test_create_user_with_specific_email()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        recovery_data = {
            "email": "ivan.login.02@mail.ru"
        }
        response = await ac.post("/api/v1/admin_panel/user/recovery_password", json=recovery_data, headers=headers)

        # Проверка на перенаправление
        if response.status_code == status.HTTP_307_TEMPORARY_REDIRECT:
            response = await ac.post(response.headers['Location'], json=recovery_data, headers=headers)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_filter_user_by_name_or_surname():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        name_filter = "John"
        params = {"name_or_surname": name_filter}

        response = await ac.get("/api/v1/admin_panel/user/", headers=headers, params=params)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Проверяем, что отфильтрованный список содержит элементы с заданным именем или фамилией
        assert isinstance(data['items'], list)
        assert len(data['items']) > 0

        for item in data['items']:
            assert name_filter in item["first_name"] or name_filter in item["last_name"]

