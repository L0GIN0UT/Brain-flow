import os
import shutil
import time
import uuid

from uuid import UUID
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, UploadFile, Query

from models.clinic import Clinic, ClinicCreate, ClinicRead
from service import common, service_users
from db.postgres import get_session, AsyncSession
from config.logs_config import logger_app_clinic
from starlette.responses import FileResponse

router = APIRouter(
    prefix='/api/v1/admin_panel/clinic',
    tags=['Панель администратора - Раздел Клиника'],
    dependencies=[Depends(service_users.check_admin_status)]
)


@router.get(
    '/',
    response_model=list[Clinic],
    summary="Список Клиник",
    description="Список Клиник зарегистрированных в системе",
    response_description="Список Клиник в системе"
)
# @cache(key_builder=redis_persons_key_by_id)
async def clinic_list(
        session: AsyncSession = Depends(get_session)
) -> list[Clinic]:
    result, err = await common.get_models_list(models_type=Clinic, session=session)
    if err:
        logger_app_clinic.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return [*result]


@router.get(
    '/{clinic_uuid}',
    response_model=ClinicRead,
    summary="Раздел Клиники",
    description="Карточка Клиники",
    response_description="Данные Клиники"
)
# @cache(key_builder=redis_persons_key_by_id)
async def clinic_details(
        clinic_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> Clinic | list:
    result, err = await common.get_model_details(model_uuid=clinic_uuid, model_type=Clinic, session=session)
    if err:
        logger_app_clinic.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.post(
    '/registration',
    response_model=Clinic,
    summary="Регистрация клиники",
    description="Регистрация новой клиники",
    response_description="Данные зарегистрированой клиники"
)
# @cache(key_builder=redis_persons_key_by_id)
async def create_clinic(
        clinic_write_model: ClinicCreate,
        session: AsyncSession = Depends(get_session)
) -> Clinic:
    exam, err = await common.get_models_list(models_type=Clinic, session=session)
    if err:
        logger_app_clinic.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err)
    if not exam:
        result, err = await common.write_model_to_database(model_to_write=clinic_write_model, model_type=Clinic,
                                                           session=session)
        if err:
            logger_app_clinic.error(f"ERROR: {err}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"ERROR: {err}")
        return result
    else:
        logger_app_clinic.error("You cannot create more than one clinic")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='You cannot create more than one clinic')


@router.put(
    '/{clinic_uuid}',
    response_model=Clinic,
    summary="Обновление Клиники",
    description="Обновление карточки Клиники",
    response_description="Обновленная карточка Клиники"
)
# @cache(key_builder=redis_persons_key_by_id)
async def clinic_update(
        clinic_uuid: UUID,
        model_to_write: ClinicCreate,
        session: AsyncSession = Depends(get_session)
) -> Clinic | list:
    result, err = await common.update_model_in_database(model_uuid=clinic_uuid, model_type=Clinic,
                                                        model_to_update=model_to_write, session=session)
    if err:
        logger_app_clinic.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.delete(
    '/{clinic_uuid}',
    summary="Удаление Клиники",
    description="Удаление карточки Клиники",
    response_description="Успешное удаление"
)
# @cache(key_builder=redis_persons_key_by_id)
async def clinic_delete(
        clinic_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> None:
    await common.delete_model_clinic(clinic_uuid=clinic_uuid, session=session)


@router.post("/logo",
             summary="Загрузка логотипа",
             description="Загрузить логотип",
             response_description="Данные о загрузке логотипа")
async def create_upload_file(clinic_uuid: UUID, file: UploadFile, session: AsyncSession = Depends(get_session)):
    old_logo_filename, _ = await common.download_image(model=Clinic, uuid=clinic_uuid, session=session)
    old_logo_path = os.path.join('logo', old_logo_filename) if old_logo_filename else None

    compressed_file, filename, err = await common.compress_image(file)
    if err:
        logger_app_clinic.error(f"Ошибка сжатия изображения: {err}")
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=f"Ошибка сжатия изображения: {err}")

    logo, err = await common.upload_image(model=Clinic, uuid=clinic_uuid, filename=filename, session=session)
    if err:
        logger_app_clinic.error(f"Ошибка загрузки изображения: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Ошибка загрузки изображения: {err}")

    path = os.path.join('logo', filename)
    with open(path, 'wb+') as buffer:
        buffer.write(compressed_file.getbuffer())

    if old_logo_path and os.path.exists(old_logo_path):
        os.remove(old_logo_path)
        logger_app_clinic.info(f"Старый логотип {old_logo_path} удалён.")

    return {"filename": logo}


@router.get("/image/",
            summary="Получение логотипа",
            description="Получить логотип",
            response_description="Данные о получении логотипа",
            )
async def download_logo(clinic_uuid: UUID = Depends(common.get_clinic_uuid),
                        t: float = Query(default=None),
                        session: AsyncSession = Depends(get_session)):
    path, err = await common.download_image(model=Clinic, uuid=clinic_uuid, session=session)
    app_dir = os.getenv("APP_DIR", "/app")
    full_path = os.path.join(app_dir, "logo", path)
    if err:
        logger_app_clinic.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not path or not os.path.exists(full_path):
        logger_app_clinic.error(f"Файл по пути {full_path} не найден.")
        return None

    file_response = FileResponse(full_path)

    # Добавляем заголовки для предотвращения кэширования
    file_response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    file_response.headers["Pragma"] = "no-cache"
    file_response.headers["Expires"] = "0"

    return file_response
