from uuid import UUID
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException

from models.clinicaddress import ClinicAddress, ClinicAddressCreate, ClinicAddressUpdate
from service import common, service_users
from db.postgres import get_session, AsyncSession
from config.logs_config import logger_app_clinic_address


router = APIRouter(
    prefix='/api/v1/admin_panel/clinic_address',
    tags=['Панель администратора - Раздел Адрес клиники'],
    dependencies=[Depends(service_users.check_admin_status)]
)


@router.get(
    '/',
    response_model=list[ClinicAddress] | list,
    summary="Список адресов клиник",
    description="Список адресов клиник зарегистрированных в системе",
    response_description="Список адресов клиник в системе"
)
# @cache(key_builder=redis_persons_key_by_id)
async def clinic_address_list(
        session: AsyncSession = Depends(get_session)
) -> list[ClinicAddress] | list:
    result, err = await common.get_models_list(models_type=ClinicAddress, session=session)
    if err:
        logger_app_clinic_address.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.get(
    '/{clinic_address_uuid}',
    response_model=ClinicAddress,
    summary="Раздел адрес клиники",
    description="Карточка адреса Клиники с ворзможностью редактировать и обновлять данные",
    response_description="Данные адреса клиники"
)
# @cache(key_builder=redis_persons_key_by_id)
async def clinic_address_details(
        clinic_address_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> ClinicAddress | list:
    result, err = await common.get_model_details(model_uuid=clinic_address_uuid, model_type=ClinicAddress, session=session)
    if err:
        logger_app_clinic_address.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.post(
    '/registration',
    response_model=ClinicAddress,
    summary="Регистрация адреса клиники",
    description="Регистрация нового адреса клиники",
    response_description="Данные адреса зарегистрированой клиники"
)
# @cache(key_builder=redis_persons_key_by_id)
async def create_clinic_address(
        clinic_address_write_model: ClinicAddressCreate,
        clinic_uuid: UUID = Depends(common.get_clinic_uuid),
        session: AsyncSession = Depends(get_session)
) -> ClinicAddress | list:
    new_clinic_address = ClinicAddress.from_orm(clinic_address_write_model)
    new_clinic_address.clinic_uuid = clinic_uuid
    result, err = await common.write_model_to_database(model_to_write=new_clinic_address, model_type=ClinicAddress,
                                                       session=session)
    if err:
        logger_app_clinic_address.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.put(
    '/{clinic_address_uuid}',
    response_model=ClinicAddress,
    summary="Обновление адреса клиники",
    description="Обновление карточки адреса клиники",
    response_description="Обновленная карточка адреса клиники"
)
# @cache(key_builder=redis_persons_key_by_id)
async def clinic_address_update(
        clinic_address_uuid: UUID,
        model_to_write: ClinicAddressUpdate,
        clinic_uuid: UUID = Depends(common.get_clinic_uuid),
        session: AsyncSession = Depends(get_session)
) -> ClinicAddress | list:
    new_clinic_address = ClinicAddress.from_orm(model_to_write)
    new_clinic_address.clinic_uuid = clinic_uuid
    result, err = await common.update_model_in_database(model_uuid=clinic_address_uuid, model_type=ClinicAddress,
                                                        model_to_update=new_clinic_address, session=session)
    if err:
        logger_app_clinic_address.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return []
    return result


@router.delete(
    '/{clinic_address_uuid}',
    summary="Удаление адреса клиники",
    description="Удаление карточки адреса клиники",
    response_description="Успешное удаление адреса клиники"
)
# @cache(key_builder=redis_persons_key_by_id)
async def clinic_address_delete(
        clinic_address_uuid: UUID,
        session: AsyncSession = Depends(get_session)
) -> None:
    result, err = await common.delete_model_to_database(model_uuid=clinic_address_uuid, model_type=ClinicAddress,
                                                        session=session)
    if err:
        logger_app_clinic_address.error(f"ERROR: {err}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR: {err}")
    elif not result:
        return None
    return result
