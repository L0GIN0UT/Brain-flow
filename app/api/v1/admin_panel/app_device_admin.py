from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params, paginate

from db.postgres import get_session, AsyncSession
from models.device import Device, DeviceRead, DeviceCreate, DeviceUpdate, DeviceFilter
from service import service_device, service_users, common
from config.logs_config import logger_app_device_admin
from service.common import cache_data, get_cached_data

router = APIRouter(
    prefix='/api/v1/admin_panel/devices',
    tags=['Панель администратора - Раздел Устройства'],
    dependencies=[Depends(service_users.check_admin_status)]
)


@router.get(
    '/',
    response_model=Page[DeviceRead] | list,
    summary="Список Устройств",
    description="Список устройств зарегистрированных в системе",
    response_description="Список устройств зарегистрированных в системе"
)
async def devices_list(params: Params = Depends(),
                       device_filter: DeviceFilter = FilterDepends(DeviceFilter),
                       session: AsyncSession = Depends(get_session)
                       ):
    cache_key = f"admin_devices_list_{device_filter}"
    cached_results = await get_cached_data(cache_key)
    if cached_results:
        return paginate([*cached_results], params)

    result, err = await service_device.get_devices_filter(device_filter, session)
    if err:
        logger_app_device_admin.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []

    cache_data(cache_key, result)
    return paginate([*result], params)


@router.post(
    '/registration',
    response_model=Device,
    summary="Регистрация устройства",
    description="Регистрация устройства",
    response_description="Данные зарегистрированного устройства"
)
async def create_device(
        device_write_model: DeviceCreate,
        clinic_uuid: UUID = Depends(common.get_clinic_uuid),
        session: AsyncSession = Depends(get_session)
):
    result, err = await service_device.create_device(clinic_uuid=clinic_uuid, data=device_write_model, session=session)
    if err:
        logger_app_device_admin.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.get(
    '/{device_uuid}',
    response_model=DeviceRead,
    summary="Карточка устройства",
    description="Карточка устройства",
    response_description="Карточка устройства с полями данных"
)
async def device_details(
        device_uuid: UUID,
        session: AsyncSession = Depends(get_session)
):
    result, err = await service_device.get_device(uuid=device_uuid, session=session)
    if err:
        logger_app_device_admin.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.put(
    '/{device_uuid}',
    response_model=DeviceRead,
    summary="Изменить карточку устройства",
    description="Записать в БД карточка устройства после редактирования",
    response_description="Обновленная карточка устройства с полями данных"
)
async def device_update(
        device_uuid: UUID,
        data: DeviceUpdate,
        session: AsyncSession = Depends(get_session)
):
    result, err = await service_device.update_device(uuid=device_uuid, session=session, data=data)
    if err:
        logger_app_device_admin.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.delete(
    '/{device_uuid}',
    summary="Удалить карточку устройства",
    description="Удалить из БД устройство",
    response_description="Удаленное устройство"
)
async def device_delete(
        device_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> None:
    result, err = await service_device.delete_device(uuid=device_uuid, session=session)
    if err:
        logger_app_device_admin.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return None
    return result


@router.put(
    '/switch/{device_uuid}',
    summary="Вкл/выкл устройств",
    description="Вкл/выкл устройств",
    response_description="Состояние устройств"
)
async def device_on_off(
        device_uuid: UUID,
        status: bool,
        session: AsyncSession = Depends(get_session)
):
    result = await service_device.start_stop_process(uuid=device_uuid, status=status, session=session)
    if not result:
        logger_app_device_admin.error("No result")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    return result


@router.put(
    '/calibration/{device_uuid}',
    response_model=DeviceRead,
    summary="Калибровка устройств",
    description="Определение baseline для каждого электрода устройства",
    response_description="Состояние устройств"
)
async def device_calibration(
        device_uuid: UUID,
        calibration: bool,
        calibration_time: float | None = 10,
        session: AsyncSession = Depends(get_session)
):
    result = await service_device.calibration_device(uuid=device_uuid, calibration=calibration,
                                                     calibration_time=calibration_time, session=session)
    if not result:
        logger_app_device_admin.error("No result")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    return result
