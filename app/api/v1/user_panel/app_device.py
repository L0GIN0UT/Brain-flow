from http import HTTPStatus
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params, paginate

from db.postgres import get_session, AsyncSession
from models.device import Device, DeviceRead, DeviceFilterNoType
from service import service_device, service_users
from config.logs_config import logger_app_device
from service.common import cache_data, get_cached_data

router = APIRouter(
    prefix='/api/v1/devices',
    tags=['Панель пользователя - Раздел Устройства'],
    dependencies=[Depends(service_users.get_current_user_uuid)]
)


@router.get(
    '/',
    response_model=Page[Device],
    summary="Список Устройств",
    description="Список устройств зарегистрированных в системе",
    response_description="Список устройств зарегистрированных в системе"
)
async def devices_list(params: Params = Depends(),
                       device_filter: DeviceFilterNoType = FilterDepends(DeviceFilterNoType),
                       session: AsyncSession = Depends(get_session)):

    cache_key = f"devices_list_{device_filter}"
    cached_results = await get_cached_data(cache_key)
    if cached_results:
        return paginate([*cached_results], params)

    result, err = await service_device.get_devices_filter(device_filter, session)
    if err:
        logger_app_device.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []

    try:
        await cache_data(cache_key, result)
    except Exception as e:
        logger_app_device.error(f"Ошибка при кэшировании данных: {e}")

    return paginate([*result], params)


@router.get(
    '/{device_uuid}',
    response_model=Device,
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
        logger_app_device.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.put(
    '/switch/{device_uuid}',
    response_model=DeviceRead,
    summary="Вкл/выкл устройств",
    description="Вкл/выкл устройств",
    response_description="Состояние устройств"
)
async def device_on_off(
        device_uuid: UUID,
        status: bool,
        session: AsyncSession = Depends(get_session)
):
    result, err = await service_device.start_stop_process(uuid=device_uuid, status=status, session=session)
    if err:
        logger_app_device.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    if not result:
        logger_app_device.error(f"INTERNAL SERVER ERROR: result {result}")
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
        logger_app_device.error(f"INTERNAL SERVER ERROR")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    return result
