from uuid import UUID
from http import HTTPStatus
from fastapi_filter import FilterDepends
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params, paginate

from models.type_research import TypeResearch, TypeResearchCreate, TypeResearchFilter
from service import common, service_users
from db.postgres import get_session, AsyncSession
from config.logs_config import logger_app_type_research

router = APIRouter(
    prefix='/api/v1/type_research',
    tags=['Панель пользователя - Раздел тип исследования'],
    dependencies=[Depends(service_users.get_current_user_uuid)]
)


@router.get(
    '/',
    response_model=Page[TypeResearch] | list,
    summary="Список исследований",
    description="Список исследований зарегистрированных в системе",
    response_description="Список исследований в системе"
)
# @cache(key_builder=redis_persons_key_by_id)
async def type_research_list(
        params: Params = Depends(),
        type_research_filter: TypeResearchFilter = FilterDepends(TypeResearchFilter),
        session: AsyncSession = Depends(get_session)
) -> list[TypeResearch] | list:
    result, err = await common.search(TypeResearch, type_research_filter, session)
    if err:
        logger_app_type_research.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return paginate([*result], params)


@router.get(
    '/{type_research_uuid}',
    response_model=TypeResearch,
    summary="Раздел тип исследования",
    description="Карточка о типе исследования",
    response_description="Данные о типе исследования"
)
async def type_research_details(
        type_research_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> TypeResearch | list:
    result, err = await common.get_model_details(model_uuid=type_research_uuid, model_type=TypeResearch,
                                                 session=session)
    if err:
        logger_app_type_research.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.post(
    '/registration',
    response_model=TypeResearch,
    summary="Регистрация типа исследования",
    description="Регистрация нового типа исследования",
    response_description="Данные о типе исследования"
)
async def create_type_research(
        type_research_write_model: TypeResearchCreate,
        session: AsyncSession = Depends(get_session)
) -> TypeResearch | list:
    result, err = await common.write_model_to_database(model_to_write=type_research_write_model,
                                                       model_type=TypeResearch,
                                                       session=session)
    if err:
        logger_app_type_research.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.put(
    '/{type_research_uuid}',
    response_model=TypeResearch,
    summary="Обновление данных о типе исследования",
    description="Обновление карточки данных о типе исследования",
    response_description="Обновленная карточка данных о типе исследования"
)
async def type_research_update(
        type_research_uuid: UUID,
        model_to_write: TypeResearchCreate,
        session: AsyncSession = Depends(get_session)
) -> TypeResearch | list:
    result, err = await common.update_model_in_database(model_uuid=type_research_uuid, model_type=TypeResearch,
                                                        model_to_update=model_to_write, session=session)
    if err:
        logger_app_type_research.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.delete(
    '/{type_research_uuid}',
    summary="Удаление данных о типе исследования",
    description="Удаление данных о типе исследования",
    response_description="Успешное удаление данных о типе исследования"
)
async def type_research_delete(
        type_research_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> None:
    result, err = await common.delete_model_to_database(model_uuid=type_research_uuid, model_type=TypeResearch,
                                                        session=session)
    if err:
        logger_app_type_research.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return None
    return result
