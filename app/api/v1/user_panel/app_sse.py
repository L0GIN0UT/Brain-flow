from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.requests import Request

from service import service_desync_datas_base
from config.logs_config import logger_app_sse

router = APIRouter(
    prefix='/api/v1/sse',
    tags=['Панель пользователя - Раздел Потоковая передача данных']
    # dependencies=[Depends(service_users.get_current_uuid_from_token)]
)


@router.get("/",
            summary="Потоковая передача данных",
            description="Потоковая передача данных",
            response_description="Данные"
            )
async def chart_data(request: Request, status: str = None):
    if status not in [None, "open", "in_process"]:
        logger_app_sse.error(f"Недопустимое значение статуса: '{status}'. Допустимые значения: 'open', 'in_process'.")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=f"Недопустимое значение статуса: '{status}'. Допустимые значения: 'open', 'in_process'.")
    response = StreamingResponse(service_desync_datas_base.get_data_from_rethink(request, status),
                                 media_type="text/event-stream")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@router.get("/{desync_data_uuid}",
            summary="Потоковая передача данных по исследованию",
            description="Потоковая передача данных по определенному исследованию",
            response_description="Данные"
            )
async def get_data_by_type_research_uuid(request: Request, desync_data_uuid: UUID, status: str = None):
    if status not in [None, "open", "in_process"]:
        logger_app_sse.error(f"Недопустимое значение статуса: '{status}'. Допустимые значения: 'open', 'in_process'.")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=f"Недопустимое значение статуса: '{status}'. Допустимые значения: 'open', 'in_process'.")
    response = StreamingResponse(
        service_desync_datas_base.get_data_from_rethink_by_type_research_uuid(request, desync_data_uuid, status),
        media_type="text/event-stream")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["X-Accel-Buffering"] = "no"
    return response
