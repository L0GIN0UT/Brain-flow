import os
import shutil
import time
from uuid import UUID
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Query
from fastapi.responses import FileResponse

from models.user import User, UserCreate, UserRecoveryPassword, UserRead, UserUpdate
from service import common, service_users
from db.postgres import get_session, AsyncSession
from config.logs_config import logger_app_user

router = APIRouter(
    prefix='/api/v1/user',
    tags=['Панель пользователя - Раздел Пользователь']
)


@router.get(
    '/{user_uuid}',
    response_model=UserRead,
    summary="Раздел Пользователь",
    description="Карточка данных о пользователе",
    response_description="Данные о пользователе"
)
# @cache(key_builder=redis_persons_key_by_id)
async def user_details(
        user_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> UserRead | list:
    result, err = await common.get_model_details(model_uuid=user_uuid, model_type=User, session=session)
    if err:
        logger_app_user.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.post(
    '/registration',
    response_model=UserRead,
    summary="Регистрация данных о пользователе",
    description="Регистрация новых данных о пользователе",
    response_description="Данные о пользователе"
)
# @cache(key_builder=redis_persons_key_by_id)
async def create_user(
        user_write_model: UserCreate,
        clinic_uuid: UUID = Depends(common.get_clinic_uuid),
        session: AsyncSession = Depends(get_session)
) -> User | list:
    new_user = User.from_orm(user_write_model)
    new_user.clinic_uuid = clinic_uuid
    result, err = await service_users.write_user_to_database(model_to_write=new_user, session=session)
    if err:
        logger_app_user.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.put(
    '/{user_uuid}',
    response_model=UserRead,
    summary="Обновление данных о пользователе",
    description="Обновление карточки данных о пользователе",
    response_description="Обновленная карточка данных о пользователе"
)
# @cache(key_builder=redis_persons_key_by_id)
async def user_update(
        user_uuid: UUID,
        model_to_write: UserUpdate,
        session: AsyncSession = Depends(get_session)
) -> User | list:
    result, err = await common.update_model_in_database(model_uuid=user_uuid, model_type=User,
                                                        model_to_update=model_to_write, session=session)
    if err:
        logger_app_user.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.post(
    '/recovery_password',
    summary="Восстановление пароля",
    description="восстановить пароль пользователя",
    response_description="Данные о восстановление пароля пользователем"
)
async def recovery_password_user(
        user_recovery_password_model: UserRecoveryPassword,
        session: AsyncSession = Depends(get_session)
):
    result, err = await service_users.recovery_password(user_recovery_password_model=user_recovery_password_model,
                                                        session=session)
    if err:
        logger_app_user.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.post("/avatar",
             summary="Загрузка аватара",
             description="Загрузить аватар",
             response_description="Данные о загрузке аватара")
async def create_upload_file(user_uuid: UUID, file: UploadFile, session: AsyncSession = Depends(get_session)):
    old_avatar_filename, _ = await common.download_image(model=User, uuid=user_uuid, session=session)
    old_avatar_path = os.path.join('avatar', old_avatar_filename) if old_avatar_filename else None

    compressed_file, filename, err = await common.compress_image(file)
    if err:
        logger_app_user.error(f"Ошибка сжатия изображения: {err}")
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=f"Ошибка сжатия изображения: {err}")

    avatar, err = await common.upload_image(model=User, uuid=user_uuid, filename=filename, session=session)
    if err:
        logger_app_user.error(f"Ошибка загрузки изображения: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Ошибка загрузки изображения: {err}")
    elif not avatar:
        return []

    path = os.path.join('avatar', filename)
    with open(path, 'wb+') as buffer:
        buffer.write(compressed_file.getbuffer())

    if old_avatar_path and os.path.exists(old_avatar_path):
        os.remove(old_avatar_path)
        logger_app_user.info(f"Старый аватар {old_avatar_path} удалён.")

    return {"filename": avatar}


@router.get("/image/",
            summary="Получение аватара",
            description="Получить аватар",
            response_description="Данные о получении аватара",
            )
async def download_avatar(user_uuid: UUID,
                          t: float = Query(default=None),
                          session: AsyncSession = Depends(get_session)):
    path, err = await common.download_image(model=User, uuid=user_uuid, session=session)
    app_dir = os.getenv("APP_DIR", "/app")
    full_path = os.path.join(app_dir, "avatar", path)
    if err:
        logger_app_user.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    if not full_path or not os.path.exists(full_path):
        return None
    file_path = f"avatar/{path}"
    file_response = FileResponse(file_path)

    file_response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    file_response.headers["Pragma"] = "no-cache"
    file_response.headers["Expires"] = "0"

    return file_response
