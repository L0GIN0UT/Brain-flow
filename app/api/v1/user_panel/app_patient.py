from uuid import UUID
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params, paginate

from models.patient import Patient, PatientCreate, PatientFilter, PatientRead
from service import common, service_users
from db.postgres import get_session, AsyncSession
from config.logs_config import logger_app_patient
from service.common import cache_data, get_cached_data

router = APIRouter(
    prefix='/api/v1/patient',
    tags=['Панель пользователя - Раздел Пациент'],
    dependencies=[Depends(service_users.get_current_user_uuid)]
)


@router.get(
    '/',
    response_model=Page[Patient] | list,
    summary="Список пациентов",
    description="Список пациентов зарегистрированных в системе",
    response_description="Список пациентов в системе"
)
async def patient_list(
        params: Params = Depends(),
        patient_filter: PatientFilter = FilterDepends(PatientFilter),  # Здесь используется фильтр
        session: AsyncSession = Depends(get_session)
) -> list[Patient] | list:
    cache_key = f"patient_list_{patient_filter}"
    cached_results = await get_cached_data(cache_key)
    if cached_results:
        return paginate([*cached_results], params)

    result, err = await common.search(model=Patient, filter_model=patient_filter, session=session)
    if err:
        logger_app_patient.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []

    try:
        cache_data(cache_key, result)
    except Exception as e:
        logger_app_patient.error(f"Ошибка при кэшировании данных: {e}")

    return paginate([*result], params)


@router.get(
    '/{patient_uuid}',
    response_model=Patient,
    summary="Раздел Пациент",
    description="Карточка данных о пациенте",
    response_description="Данные о пациенте"
)
# @cache(key_builder=redis_persons_key_by_id)
async def patient_details(
        patient_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> Patient | list:
    result, err = await common.get_model_details(model_uuid=patient_uuid, model_type=Patient, session=session)
    if err:
        logger_app_patient.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.post(
    '/registration',
    response_model=Patient,
    summary="Регистрация данных о пациенте",
    description="Регистрация новых данных о пациенте",
    response_description="Данные о пациенте"
)
# @cache(key_builder=redis_persons_key_by_id)
async def create_patient(
        patient_write_model: PatientCreate,
        clinic_uuid: UUID = Depends(common.get_clinic_uuid),
        session: AsyncSession = Depends(get_session)
) -> Patient | list:
    new_patient = Patient.from_orm(patient_write_model)
    new_patient.clinic_uuid = clinic_uuid
    result, err = await common.write_model_to_database(model_to_write=new_patient, model_type=Patient,
                                                       session=session)
    if err:
        logger_app_patient.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.put(
    '/{patient_uuid}',
    response_model=Patient,
    summary="Обновление данных о пациенте",
    description="Обновление карточки данных о пациенте",
    response_description="Обновленная карточка данных о пациенте"
)
# @cache(key_builder=redis_persons_key_by_id)
async def patient_update(
        patient_uuid: UUID,
        model_to_write: PatientRead,
        session: AsyncSession = Depends(get_session)
) -> Patient | list:
    result, err = await common.update_model_in_database(model_uuid=patient_uuid, model_type=Patient,
                                                        model_to_update=model_to_write, session=session)
    if err:
        logger_app_patient.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.delete(
    '/{patient_uuid}',
    summary="Удаление данных о пациенте",
    description="Удаление данных о пациенте",
    response_description="Успешное удаление данных о пациенте"
)
async def patient_delete(
        patient_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> None:
    result, err = await common.delete_model_to_database(model_uuid=patient_uuid, model_type=Patient, session=session)
    if err:
        logger_app_patient.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return None
    return result
