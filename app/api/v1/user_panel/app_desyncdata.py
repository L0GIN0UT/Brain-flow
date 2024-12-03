from uuid import UUID
from http import HTTPStatus
from typing import List, Union
from datetime import datetime
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params, paginate

from models.desyncdata import DesyncDatas, DesyncDatasCreate, DesyncDatasRead, DesyncDatasBaseWithoutData
from service import common, service_desync_datas_base
from db.postgres import get_session, AsyncSession
from service import service_users
from config.logs_config import logger_app_desyncdata
from service.common import cache_data, get_cached_data

router = APIRouter(
    prefix='/api/v1/desync_datas',
    tags=['Панель пользователя - Раздел Исследования'],
    dependencies=[Depends(service_users.get_current_user_uuid)]
)


@router.post(
    '/registration',
    response_model=DesyncDatasRead,
    summary="Регистрация данных исследования",
    description="Регистрация новых данных исследования",
    response_description="Данные данных исследования"
)
async def create_datas(data: DesyncDatasCreate,
                       duration: int,
                       session: AsyncSession = Depends(get_session)) -> DesyncDatasRead | list:
    result, err = await service_desync_datas_base.create_research(data=data, duration=duration, session=session)
    if err:
        logger_app_desyncdata.error(f"ERROR: {err}")
        if err == 1:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Это устройство уже используется в другом активном исследовании.")
        else:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    result = DesyncDatasRead.from_orm(result)
    return result

@router.get(
    '/desync_user',
    response_model=Page[DesyncDatasBaseWithoutData] | list,
    summary="История исследований для пользователя",
    description="История исследований для пользователя с сортировкой",
    response_description="Найденные записи с историей пользователем"
)
async def desync_users(user_uuid: str = Depends(service_users.get_current_user_uuid),
                       device_uuid: str | None = None,
                       type_research_uuid: str | None = None,
                       date_from: str | None = None,
                       date_to: str | None = None,
                       patient_uuid: str | None = None,
                       research_uuid_part: str | None = None,
                       params: Params = Depends(),
                       session: AsyncSession = Depends(get_session)
                       ) -> list[DesyncDatasBaseWithoutData] | list:

    device_uuid = common.validate_uuid(device_uuid)
    type_research_uuid = common.validate_uuid(type_research_uuid)
    patient_uuid = common.validate_uuid(patient_uuid)

    cache_key = f"research_history_user_{user_uuid}_{device_uuid}_{type_research_uuid}_{date_from}_{date_to}_{patient_uuid}"
    try:
        cached_results = await get_cached_data(cache_key)
        if cached_results:
            unique_results = {item['uuid']: item for item in cached_results}.values()
            return paginate(list(unique_results), params)
    except Exception as e:
        logger_app_desyncdata.debug(f"Ошибка при работе с кэшированными данными: {e}")
    results, err = await service_desync_datas_base.view_history(user_uuid, session, device_uuid,
                                                                type_research_uuid, date_from,
                                                                date_to, patient_uuid, research_uuid_part)
    if err:
        logger_app_desyncdata.debug(f"Проверьте правильность введенных данных. ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=f"Проверьте правильность введенных данных. ERROR: {err}")
    elif not results:
        return []
    try:
        results_dicts = [item.dict() for item in results]
        cache_data(cache_key, results_dicts)
    except Exception as e:
        logger_app_desyncdata.debug(f"Ошибка при кэшировании данных: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Ошибка при кэшировании данных")
    return paginate([*results], params)



@router.get(
    '/{desync_uuid}',
    response_model=DesyncDatas,
    summary="Карточка исследования",
    description="Карточка с информацией о проводившемся исследовании",
    response_description="Карточка исследования с полями данных"
)
async def desync_details(
        desync_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> DesyncDatas | list:
    result, err = await common.get_model_details(model_uuid=desync_uuid, model_type=DesyncDatas, session=session)
    if err:
        logger_app_desyncdata.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result
