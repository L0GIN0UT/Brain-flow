import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
import uuid

from tests.conftest import get_auth_token


@pytest.mark.asyncio
async def test_register_patient():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        new_patient = {
            "code": f"P{uuid.uuid4().hex[:6]}",  # Генерация уникального кода
            "diagnosis": "Test Diagnosis"
        }

        response = await ac.post("/api/v1/patient/registration", json=new_patient, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "uuid" in data
        assert data["code"] == new_patient["code"]
        assert data["diagnosis"] == new_patient["diagnosis"]

        # Проверяем данные пациента через GET запрос
        response = await ac.get(f"/api/v1/patient/{data['uuid']}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        patient_data = response.json()
        assert patient_data["code"] == new_patient["code"]
        assert patient_data["diagnosis"] == new_patient["diagnosis"]
        return data["uuid"]


@pytest.mark.asyncio
async def test_update_patient():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Регистрируем пациента и получаем его UUID
        patient_uuid = await test_register_patient()

        # Повторная аутентификация для обновления токена
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        updated_data = {
            "code": f"P{uuid.uuid4().hex[:6]}",  # Генерация уникального кода
            "diagnosis": "Updated Diagnosis"
        }

        response = await ac.put(f"/api/v1/patient/{patient_uuid}", json=updated_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == updated_data["code"]
        assert data["diagnosis"] == updated_data["diagnosis"]

        # Проверяем, что данные пациента обновлены
        response = await ac.get(f"/api/v1/patient/{patient_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        patient_data = response.json()
        assert patient_data["code"] == updated_data["code"]
        assert patient_data["diagnosis"] == updated_data["diagnosis"]


@pytest.mark.asyncio
async def test_delete_patient():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        patient_uuid = await test_register_patient()

        # Повторная аутентификация для удаления пациента
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        response = await ac.delete(f"/api/v1/patient/{patient_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        # Проверяем, что пациента больше не существует
        response = await ac.get(f"/api/v1/patient/{patient_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["uuid"] is None
        assert data["code"] is None
        assert data["diagnosis"] is None
        assert data["clinic_uuid"] is None


@pytest.mark.asyncio
async def test_filter_patients_by_code():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        patient_code = "888"
        params = {"code": patient_code}

        response = await ac.get("/api/v1/patient/", headers=headers, params=params)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ
        data = response.json()
        assert isinstance(data['items'], list)  # Проверяем, что ответ является списком
        assert len(data['items']) > 0  # Проверяем, что список не пустой

        # Проверяем, что все пациенты имеют код "888"
        for patient in data['items']:
            assert patient["code"] == patient_code
