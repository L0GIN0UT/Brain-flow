import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
from models.settings import SettingsUpdate
from tests.conftest import get_auth_token

@pytest.mark.asyncio
async def test_get_settings():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/api/v1/admin_panel/settings/", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ
        data = response.json()
        assert isinstance(data, dict)  # Проверяем, что данные представляют собой словарь
        assert "BORDER_TIME" in data  # Проверяем наличие некоторых ожидаемых полей


@pytest.mark.asyncio
async def test_update_settings():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Получаем текущие настройки для их восстановления после теста
        response = await ac.get("/api/v1/admin_panel/settings/", headers=headers)
        original_settings = response.json()

        # Обновляем настройки
        updated_settings_data = {
            "BORDER_TIME": 100,
            "FIVE_MINUTE_SAMPLE": 300,
            "USE_IMPEDANCE": 1,
            "MAX_SAMPLES": 50,
            "LOG_LEVEL": "DEBUG",
            "MAIL_ADDRESS": "test@example.com",
            "MAIL_SMTP_SERVER": "smtp.example.com",
            "MAIL_PORT": 587,
            "MAIL_MESSAGE_SUBJECT": "Test Subject",
            "MAIL_MESSAGE_TEXT": "Test Message"
        }
        response = await ac.put("/api/v1/admin_panel/settings/", json=updated_settings_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ
        data = response.json()

        # Приведение типов данных для сравнения
        assert int(data["BORDER_TIME"]) == 100
        assert int(data["FIVE_MINUTE_SAMPLE"]) == 300
        assert int(data["USE_IMPEDANCE"]) == 1
        assert int(data["MAX_SAMPLES"]) == 50
        assert data["LOG_LEVEL"] == "DEBUG"
        assert data["MAIL_ADDRESS"] == "test@example.com"
        assert data["MAIL_SMTP_SERVER"] == "smtp.example.com"
        assert int(data["MAIL_PORT"]) == 587
        assert data["MAIL_MESSAGE_SUBJECT"] == "Test Subject"
        assert data["MAIL_MESSAGE_TEXT"] == "Test Message"

        # Восстанавливаем оригинальные настройки
        response = await ac.put("/api/v1/admin_panel/settings/", json=original_settings, headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ