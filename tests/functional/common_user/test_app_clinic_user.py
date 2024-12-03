import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
from tests.conftest import get_auth_token


@pytest.mark.asyncio
async def test_get_clinic_list():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/api/v1/clinic/", headers=headers)

        assert response.status_code == status.HTTP_200_OK  # Проверка успешного ответа
        data = response.json()

        # Проверка структуры и содержимого ответа
        assert isinstance(data, list), "Response data should be a list"
        assert len(data) > 0, "Clinic list should not be empty"

        for clinic in data:
            assert "uuid" in clinic, "Each clinic should have a UUID"
            assert "name" in clinic and isinstance(clinic["name"], str), "Each clinic should have a valid name"
            assert "description" in clinic and isinstance(clinic["description"],
                                                          str), "Each clinic should have a valid description"
            assert "logo" in clinic and isinstance(clinic["logo"], str), "Each clinic should have a valid logo"

        return data[0]["uuid"]  # Возвращаем UUID первой клиники


@pytest.mark.asyncio
async def test_download_avatar():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Получаем UUID клиники через отдельный запрос, чтобы токен был актуальным
        clinic_uuid = await test_get_clinic_list()

        # Повторно получаем токен, чтобы убедиться, что он актуален
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        response = await ac.get(f"/api/v1/clinic/image/?clinic_uuid={clinic_uuid}", headers=headers)

        # Проверка на наличие ошибок при запросе изображения
        assert response.status_code == status.HTTP_200_OK, f"Failed to get image. Response: {response.text}"

        # Проверка типа контента, чтобы убедиться, что это изображение
        assert response.headers["content-type"] == "image/png", "Content type should be 'image/png'"

        # Проверка, что тело ответа не пустое (хотя бы минимальная проверка на размер)
        assert len(response.content) > 0, "Image content should not be empty"

