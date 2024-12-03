import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
import uuid


@pytest.mark.asyncio
async def test_streaming_data():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        async with ac.stream("GET", "/api/v1/sse/?status=open") as response:
            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"].startswith("text/event-stream")
            assert response.headers["Access-Control-Allow-Origin"] == "*"
            assert response.headers["X-Accel-Buffering"] == "no"

            # Читаем часть данных из потока
            first_chunk = await response.aiter_text().__anext__()  # Читаем первый блок данных
            assert first_chunk is not None


@pytest.mark.asyncio
async def test_streaming_data_by_uuid():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        test_uuid = str(uuid.uuid4())
        async with ac.stream("GET", f"/api/v1/sse/{test_uuid}?status=open") as response:
            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"].startswith("text/event-stream")
            assert response.headers["Access-Control-Allow-Origin"] == "*"
            assert response.headers["X-Accel-Buffering"] == "no"

            # Читаем часть данных из потока
            first_chunk = await response.aiter_text().__anext__()  # Читаем первый блок данных
            assert first_chunk is not None
