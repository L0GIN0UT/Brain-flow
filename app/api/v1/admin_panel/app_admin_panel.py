"""
Response:
# клиника:
#"name": "string",
#"logo": "string",
#"uuid": "uuid"
#
# пользователи:
#"last_name": "string",
#"first_name": "string",
#"patronymic": "string",
#"avatar": "string"
#
# устройства:
#"name": "string",
#"status": "bool" - получать из rethink
#типы устройств:
#"name": "string"
#
# виды реабилитации:
#"name": "string"
"""

from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException

from db.postgres import get_session, AsyncSession
from models.admin_panel import AdminPanel
from models.clinic import Clinic
from models.type_research import TypeResearch
from models.user import User
from models.device_type import DeviceType
from service import common, service_device

router = APIRouter(
    prefix='/api/v1/admin_panel',
    tags=['Панель администратора']
)


@router.get(
    '/',
    response_model=AdminPanel,
    summary="Панель администратора",
    description="Панель администратора с информацией",
    response_description="Списки пользователей, устройств, типов устройств, видов реабилитации"
                         "зарегистрированных в системе"
)
# @cache(key_builder=redis_persons_key_by_id)
async def admin_panel_list(session: AsyncSession = Depends(get_session)):
    device_status,error = await service_device.devices_status()
    result, err = await common.get_admin_panel_list(session=session,
                                                    clinic=Clinic,
                                                    users=User,
                                                    type_research=TypeResearch,
                                                    device_types=DeviceType)

    if err:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, details=f"ERROR: {err}")
    if error:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, details=f"ERROR: {error}")
    elif not result:
        return []
    result['devices'] = [*device_status.items]
    return result

