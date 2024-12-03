from fastapi import APIRouter

router = APIRouter(
    prefix='/api/v1/admin_panel/settings',
    tags=['Панель администратора - Раздел Настройки']
)


@router.get(
    '/',
    # response_model=Users
    summary="Раздел Настройки",
    description="Настройки системы",
    response_description="Словарь с настройками"
)
# @cache(key_builder=redis_persons_key_by_id)
def settings_list(
        # session: Session = Depends(get_session)
        # person_id: UUID,
        # person_service: PersonService = Depends(get_service)
) -> dict:
    pass
