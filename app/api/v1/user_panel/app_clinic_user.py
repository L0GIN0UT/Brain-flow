from http import HTTPStatus
from uuid import UUID
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from models.clinic import Clinic
from service import common, service_users
from db.postgres import get_session, AsyncSession
from config.logs_config import logger_app_clinic_user

router = APIRouter(
    prefix='/api/v1/clinic',
    tags=['Панель пользователя - Раздел Клиника'],
    dependencies=[Depends(service_users.get_current_user_uuid)]
)


@router.get(
    '/',
    response_model=list[Clinic] | list,
    summary="Список Клиник",
    description="Список Клиник зарегистрированных в системе",
    response_description="Список Клиник в системе"
)
async def clinic_list(
        session: AsyncSession = Depends(get_session)
) -> list[Clinic] | list:
    result, err = await common.get_models_list(models_type=Clinic, session=session)
    if err:
        logger_app_clinic_user.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return [*result]


@router.get("/image/",
            summary="Получение логотипа",
            description="Получить логотип",
            response_description="Данные о получении логотипа",
            )
async def download_avatar(clinic_uuid: UUID = Depends(common.get_clinic_uuid),
                          session: AsyncSession = Depends(get_session)):
    path, err = await common.download_image(model=Clinic, uuid=clinic_uuid, session=session)
    app_dir = os.getenv("APP_DIR", "/app")
    full_path = os.path.join(app_dir, "logo", path)
    logger_app_clinic_user.info(f"Full path to logo: {full_path}")
    if err:
        logger_app_clinic_user.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not path or not os.path.exists(full_path):
        logger_app_clinic_user.error(f"File at path {full_path} does not exist.")
        # return FileResponse(os.path.join(app_dir, "logo/default_logo.png"))
        return None
    return FileResponse(full_path)
