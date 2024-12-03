from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from http import HTTPStatus

from models.settings import SettingsUpdate
from service import service_settings, service_users
from db.postgres import get_session, AsyncSession
from config.logs_config import logger_app_settings

router = APIRouter(
    prefix='/api/v1/admin_panel/settings',
    tags=['Панель администратора - Настройки'],
    dependencies=[Depends(service_users.check_admin_status)]
)


@router.get(
    '/',
    response_model=dict,
    summary="Текущие настройки",
    description="Получение текущих настроек из .env файла",
    response_description="Настройки"
)
async def get_settings():
    settings, err = service_settings.read_settings()
    if err:
        print(f"ERROR: {err}")
        logger_app_settings.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    return settings


@router.put(
    '/',
    response_model=dict,
    summary="Обновление настроек",
    description="Обновление настроек в .env файле",
    response_description="Обновленные настройки"
)
async def update_settings(
        settings_update: SettingsUpdate,
        session: AsyncSession = Depends(get_session)
):
    updated_settings, err = await service_settings.update_settings(settings_update)
    if err:
        print(f"ERROR: {err}")
        logger_app_settings.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"ERROR: {err}")
    return updated_settings
