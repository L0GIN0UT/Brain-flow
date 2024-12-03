import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
from tests.conftest import get_auth_token
import uuid


@pytest.mark.asyncio
async def test_get_patients_list():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/api/v1/admin_panel/patient/", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ
        data = response.json()

        # Проверяем общую структуру ответа
        assert isinstance(data['items'], list)
        assert data["total"] > 0
        assert data["page"] == 1
        assert data["size"] > 0
        assert data["pages"] >= 1

        # Проверяем каждый элемент в списке
        for item in data['items']:
            assert "uuid" in item and isinstance(item["uuid"], str)
            assert "code" in item and isinstance(item["code"], str)
            assert "diagnosis" in item and isinstance(item["diagnosis"], str)
            assert "clinic_uuid" in item and isinstance(item["clinic_uuid"], str)


@pytest.mark.asyncio
async def test_create_patient():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Создаем новый уникальный код пациента
        unique_code = f"Patient_{uuid.uuid4()}"
        new_patient_data = {
            "code": unique_code,
            "diagnosis": "Test Diagnosis"
        }
        response = await ac.post("/api/v1/admin_panel/patient/registration", json=new_patient_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        data = response.json()
        assert data["code"] == unique_code
        assert data["diagnosis"] == "Test Diagnosis"

        # Проверяем, что пациент был добавлен в список
        patient_uuid = data["uuid"]
        list_response = await ac.get("/api/v1/admin_panel/patient/", headers=headers)
        list_data = list_response.json()
        assert any(item["uuid"] == patient_uuid for item in list_data["items"])

        return patient_uuid  # Возвращаем UUID нового пациента для использования в других тестах


@pytest.mark.asyncio
async def test_get_patient_details():
    patient_uuid = await test_create_patient()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        response = await ac.get(f"/api/v1/admin_panel/patient/{patient_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Проверяем структуру и значения ответа
        assert data["uuid"] == patient_uuid
        assert "code" in data and isinstance(data["code"], str)
        assert "diagnosis" in data and isinstance(data["diagnosis"], str)
        assert "clinic_uuid" in data and isinstance(data["clinic_uuid"], str)


@pytest.mark.asyncio
async def test_update_patient():
    patient_uuid = await test_create_patient()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Обновляем данные пациента
        updated_data = {
            "code": "Updated Patient Code",
            "diagnosis": "Updated Diagnosis"
        }
        response = await ac.put(f"/api/v1/admin_panel/patient/{patient_uuid}", json=updated_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        # Проверяем, что данные обновились
        updated_response = await ac.get(f"/api/v1/admin_panel/patient/{patient_uuid}", headers=headers)
        updated_data_response = updated_response.json()

        assert updated_data_response["code"] == "Updated Patient Code"
        assert updated_data_response["diagnosis"] == "Updated Diagnosis"


@pytest.mark.asyncio
async def test_delete_patient():
    patient_uuid = await test_create_patient()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        token = await get_auth_token(ac)
        headers = {"Authorization": f"Bearer {token}"}

        # Удаляем пациента
        response = await ac.delete(f"/api/v1/admin_panel/patient/{patient_uuid}", headers=headers)
        assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный ответ

        # Проверяем, что данные пациента очищены
        check_response = await ac.get(f"/api/v1/admin_panel/patient/{patient_uuid}", headers=headers)
        assert check_response.status_code == status.HTTP_200_OK
        data = check_response.json()
        assert data["code"] is None
        assert data["diagnosis"] is None
        assert data["clinic_uuid"] is None
        assert data["uuid"] is None
