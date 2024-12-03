from uuid import UUID
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params, paginate

from db.postgres import get_session, AsyncSession
from models.device_type import DeviceType, DeviceTypeCreate, DeviceTypeFilter
from service import common, service_users, service_device_type
from config.logs_config import logger_app_device_type

router = APIRouter(
    prefix='/api/v1/admin_panel/devices_type',
    tags=['Панель администратора - Раздел - Типы устройств'],
    dependencies=[Depends(service_users.check_admin_status)]
)


@router.get(
    '/',
    response_model=Page[DeviceType] | list,
    summary="Список типов устройств",
    description="Список типов устройств зарегистрированных в системе",
    response_description="Список типов устройств зарегистрированных в системе"
)
async def devices_type_list(
    params: Params = Depends(),
    device_type_filter: DeviceTypeFilter = FilterDepends(DeviceTypeFilter),
    session: AsyncSession = Depends(get_session)
) -> list[DeviceType] | list:
    result, err = await service_device_type.get_device_types_filter(device_type_filter, session)
    if err:
        logger_app_device_type.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return paginate([*result], params)


@router.post(
    '/registration',
    response_model=DeviceType,
    summary="Регистрация типа устройства",
    description="Регистрация типа устройства",
    response_description="тип зарегистрированного устройства"
)
# @cache(key_builder=redis_persons_key_by_id)
async def create_device_type(
        device_type_write_model: DeviceTypeCreate,
        session: AsyncSession = Depends(get_session)
) -> DeviceType | list:
    result, err = await common.write_model_to_database(model_to_write=device_type_write_model, model_type=DeviceType,
                                                       session=session)
    if err:
        logger_app_device_type.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.get(
    '/{device_type_uuid}',
    response_model=DeviceType,
    summary="Карточка типа устройства",
    description="Карточка типа устройства  ",
    response_description="Карточка типа устройства с полями данных"
)
# @cache(key_builder=redis_persons_key_by_id)
async def device_type_details(
        device_type_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> DeviceType | list:
    result, err = await common.get_model_details(model_uuid=device_type_uuid, model_type=DeviceType, session=session)
    if err:
        logger_app_device_type.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.put(
    '/{device_type_uuid}',
    summary="Изменить карточку типа устройства",
    description="Записать в БД карточку типа устройства после редактирования",
    response_description="Обновленная карточка типа устройства с полями данных"
)
# @cache(key_builder=redis_persons_key_by_id)
async def device_type_update(
        device_type_uuid: UUID,
        model_to_write: DeviceTypeCreate,
        session: AsyncSession = Depends(get_session)
) -> DeviceType | list:
    result, err = await common.update_model_in_database(model_uuid=device_type_uuid, model_type=DeviceType,
                                                        model_to_update=model_to_write, session=session)
    if err:
        logger_app_device_type.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.delete(
    '/{device_type_uuid}',
    summary="Удалить карточку типа устройства",
    description="Удалить из БД карточку типа устройства",
    response_description="Подтверждение удаления"
)
# @cache(key_builder=redis_persons_key_by_id)
async def device_type_delete(
        device_type_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> None:
    result, err = await common.delete_model_to_database(model_uuid=device_type_uuid, model_type=DeviceType, session=session)
    if err:
        logger_app_device_type.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return None
    return result
