from uuid import UUID
from http import HTTPStatus
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params, paginate

from models.desyncdata import DesyncDatas, DesyncDatasCreate, DesyncDatasBaseWithoutData
from service import common, service_desync_datas_base
from db.postgres import get_session, AsyncSession
from service import service_users
from config.logs_config import logger_app_desyncdata_admin
from service.common import cache_data, get_cached_data, custom_serializer

router = APIRouter(
    prefix='/api/v1/admin_panel/desync_datas',
    tags=['Панель администратора - Раздел Исследования'],
    dependencies=[Depends(service_users.check_admin_status)]
)


@router.get(
    '/',
    response_model=Page[DesyncDatasBaseWithoutData] | list,
    summary="История исследований",
    description="История проведенных исследований",
    response_description="Список проведенных исследований"
)
async def desync_users(user_uuid: str | None = None,
                       device_uuid: str | None = None,
                       type_research_uuid: str | None = None,
                       date_from: str | None = None,
                       date_to: str | None = None,
                       patient_uuid: str | None = None,
                       research_uuid_part: str | None = None,
                       params: Params = Depends(),
                       session: AsyncSession = Depends(get_session)
                       ) -> list[DesyncDatasBaseWithoutData] | list:

    user_uuid = common.validate_uuid(user_uuid)
    device_uuid = common.validate_uuid(device_uuid)
    type_research_uuid = common.validate_uuid(type_research_uuid)
    patient_uuid = common.validate_uuid(patient_uuid)

    cache_key = f"admin_research_history_{user_uuid}_{device_uuid}_{type_research_uuid}_{date_from}_{date_to}_{patient_uuid}"

    cached_results = await get_cached_data(cache_key)
    if cached_results:
        try:
            # Преобразуем кэшированные результаты в нужный формат
            unique_results = {item['uuid']: item for item in cached_results}.values()
            return paginate(list(unique_results), params)
        except Exception as e:
            logger_app_desyncdata_admin.error(f"Ошибка при работе с кэшированными данными: {e}")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail="Ошибка при работе с кэшированными данными")

    results, err = await service_desync_datas_base.view_history(user_uuid, session, device_uuid, type_research_uuid,
                                                                date_from, date_to, patient_uuid, research_uuid_part)
    if err:
        logger_app_desyncdata_admin.error(f"Проверьте правильность введенных данных. ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=f"Проверьте правильность введенных данных. ERROR: {err}")
    elif not results:
        return []

    # Преобразуем объекты модели в словари перед сериализацией
    try:
        results_dicts = [item.dict() for item in results]  # Если это Pydantic-модель, используйте .dict()
        json_results = json.dumps(results_dicts, default=custom_serializer)
    except Exception as e:
        logger_app_desyncdata_admin.error(f"Ошибка при сериализации данных: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            detail="Ошибка при сериализации данных перед кэшированием")

    try:
        unique_results = {item['uuid']: item for item in results_dicts}.values()
        # Убираем await если функция не является асинхронной
        cache_data(cache_key, list(unique_results))  # Убедитесь, что cache_data не является coroutine
    except Exception as e:
        logger_app_desyncdata_admin.error(f"Ошибка при кэшировании данных: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Ошибка при кэшировании данных")

    return paginate(list(unique_results), params)


@router.get(
    '/{desync_uuid}',
    response_model=DesyncDatas,
    summary="Карточка исследования",
    description="Карточка с информацией о проводившимся исследовании",
    response_description="Карточка исследования с полями данных"
)
async def desync_details(
        desync_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> DesyncDatas | list:
    result, err = await common.get_model_details(model_uuid=desync_uuid, model_type=DesyncDatas, session=session)
    if err:
        logger_app_desyncdata_admin.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.put(
    '/{desync_uuid}',
    response_model=DesyncDatas,
    summary="Изменить карточку исследования",
    description="Записать в БД карточку исследования после редактирования",
    response_description="Обновленная карточка исследования с полями данных"
)
async def desync_update(
        desync_uuid: UUID,
        model_to_write: DesyncDatasCreate,
        session: AsyncSession = Depends(get_session)
) -> DesyncDatas | list:
    result, err = await common.update_model_in_database(model_uuid=desync_uuid, model_type=DesyncDatas,
                                                        model_to_update=model_to_write, session=session)
    if err:
        logger_app_desyncdata_admin.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.delete(
    '/{desync_uuid}',
    summary="Удалить данные исследования",
    description="Удалить из БД данные исследования",
    response_description="Подтверждение удаления"
)
async def desync_delete(
        desync_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> None:
    result, err = await common.delete_model_to_database(model_uuid=desync_uuid, model_type=DesyncDatas, session=session)
    if err:
        logger_app_desyncdata_admin.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return None
    return result
