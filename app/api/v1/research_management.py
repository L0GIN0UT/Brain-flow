from fastapi import APIRouter, Depends, HTTPException

# from models import user, clinic, clinicaddress, device
from models.rethink_model import DesyncLevel

router = APIRouter(
    prefix='/api/v1/research_management',
    tags=['Управление исследованиями']
)


@router.get(
    '/',
    response_model=DesyncLevel,
    summary="Управление исследованиями",
    description="Список устройств с данными дисинхронизации",
    response_description="Список устройств со шкалой дисинхронизации в реальном времени"
)
# @cache(key_builder=redis_persons_key_by_id)
def desync_devices_list(
        # session: Session = Depends(get_session)
        # person_id: UUID,
        # person_service: PersonService = Depends(get_service)
) -> DesyncLevel:
    pass


@router.get(
    '/{desync_id}',
    response_model=DesyncLevel,
    summary="Детализированная информация по десинхронизации",
    description="Детализированная информация по десинхронизации с отображением на схеме мозга",
    response_description="Значение дисинхронизации в реальном времени"
)
# @cache(key_builder=redis_persons_key_by_id)
def desync_devices_detail(
        # session: Session = Depends(get_session)
        # person_id: UUID,
        # person_service: PersonService = Depends(get_service)
) -> DesyncLevel:
    pass


@router.get(
    '/{desync_id}/eeg',
    # response_model=DesyncLevel,
    summary="ЕЕГ",
    description="Поток данных ЕЕГ в реальном времени",
    response_description="Поток ЕЕГ в реальном времени"
)
# @cache(key_builder=redis_persons_key_by_id)
def desync_devices_eeg(
        # session: Session = Depends(get_session)
        # person_id: UUID,
        # person_service: PersonService = Depends(get_service)
) -> dict:
    pass