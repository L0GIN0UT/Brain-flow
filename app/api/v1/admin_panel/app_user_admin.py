from uuid import UUID
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params, paginate

from models.user import User, UserCreate, UserRecoveryPassword, UserRead, UserUpdate
from service import common, service_users
from db.postgres import get_session, AsyncSession
from config.logs_config import logger_app_user_admin


router = APIRouter(
    prefix='/api/v1/admin_panel/user',
    tags=['Панель администратора - Раздел Пользователь'],
    dependencies=[Depends(service_users.check_admin_status)]
)


@router.get(
    '/',
    response_model=Page[UserRead] | list,
    summary="Список пользователей",
    description="Список пользователей зарегистрированных в системе",
    response_description="Список пользователей в системе"
)
# @cache(key_builder=redis_persons_key_by_id)
async def user_list(
        name_or_surname: str = None,
        params: Params = Depends(),
        session: AsyncSession = Depends(get_session)
) -> list[UserRead] | list:
    result, err = await service_users.search_user(name_or_surname=name_or_surname, session=session)
    if err:
        logger_app_user_admin.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return paginate([*result], params)


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
        logger_app_user_admin.error(f"ERROR: {err}")
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
        logger_app_user_admin.error(f"ERROR: {err}")
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
        logger_app_user_admin.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.delete(
    '/{user_uuid}',
    response_model=UserRead,
    summary="Удаление данных о пользователе",
    description="Удаление данных о пользователе",
    response_description="Успешное удаление данных о пользователе"
)
# @cache(key_builder=redis_persons_key_by_id)
async def user_delete(
        user_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> None:
    result, err = await common.delete_model_to_database(model_uuid=user_uuid, model_type=User, session=session)
    if err:
        logger_app_user_admin.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return None
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
        logger_app_user_admin.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result
