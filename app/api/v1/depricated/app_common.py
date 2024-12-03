from fastapi import APIRouter

from models.device import Device
from models.user import User

router = APIRouter(
    prefix='/api/v1/admin_panel',
    tags=['Панель администратора']
)


@router.get(
    '/',
    # response_model=Users
    summary="Панель администратора",
    description="Панель администратора для управления работой сервиса",
    response_description="Список зарегестрированных устройств и пользователей"
)
# @cache(key_builder=redis_persons_key_by_id)
def summary_list_device_users(
        # session: Session = Depends(get_session)
        # person_id: UUID,
        # person_service: PersonService = Depends(get_service)
) -> list[Device, User]:
    pass
