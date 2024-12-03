import os

import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
from uuid import uuid4

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
        response = await ac.post("/api/v1/user/registration", json=new_user_data, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["email"] == unique_email
        assert data["phone"] == unique_phone
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["patronymic"] == "Jr."
        assert data["avatar"] == unique_avatar
        assert data["profession"] == "Doctor"

        return data["uuid"], unique_phone, unique_email


@pytest.mark.asyncio
async def test_get_user_details():
    user_uuid, _, _ = await test_create_user()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get(f"/api/v1/user/{user_uuid}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["uuid"] == user_uuid
        assert "last_name" in data and isinstance(data["last_name"], str)
        assert "first_name" in data and isinstance(data["first_name"], str)
        assert "patronymic" in data and (data["patronymic"] is None or isinstance(data["patronymic"], str))
        assert "phone" in data and isinstance(data["phone"], str)
        assert "email" in data and isinstance(data["email"], str)
        assert "avatar" in data and (data["avatar"] is None or isinstance(data["avatar"], str))
        assert "profession" in data and (data["profession"] is None or isinstance(data["profession"], str))


@pytest.mark.asyncio
async def test_update_user_details():
    user_uuid, _, _ = await test_create_user()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        updated_data = {
            "last_name": "UpdatedDoe",
            "first_name": "UpdatedJohn",
            "patronymic": "UpdatedJr.",
            "phone": "+1234567890",
            "email": "updated.email@mail.ru",
            "avatar": "updated_avatar.png",
            "profession": "Updated Doctor"
        }

        response = await ac.put(f"/api/v1/user/{user_uuid}", json=updated_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["last_name"] == "UpdatedDoe"
        assert data["first_name"] == "UpdatedJohn"
        assert data["patronymic"] == "UpdatedJr."
        assert data["phone"] == "+1234567890"
        assert data["email"] == "updated.email@mail.ru"
        assert data["avatar"] == "updated_avatar.png"
        assert data["profession"] == "Updated Doctor"


@pytest.mark.asyncio
async def test_recovery_password():
    await test_create_user()  # Создаем пользователя для восстановления пароля

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        recovery_data = {
            "email": "ivan.login.02@mail.ru"
        }
        response = await ac.post("/api/v1/user/recovery_password", json=recovery_data, headers=headers)

        assert response.status_code == status.HTTP_200_OK
