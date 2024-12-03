import json
import socket
from typing import Iterator, List, Optional, AsyncGenerator
import asyncio
import datetime as DT
from uuid import UUID

from sqlalchemy import exc
from fastapi import HTTPException
from requests import RequestException
from rethinkdb import r
from fastapi.requests import Request
from sqlalchemy.future import select

from config.settings import settings
from db.postgres import get_session, AsyncSession
from models.desyncdata import DesyncDatas, DesyncDatasCreate
from db.rethink import get_rethink_session
from models.patient import Patient
from sqlalchemy.future import select
from sqlalchemy import exc, or_, text

db = settings.rethinkdb_db
table = settings.rethinkdb_table


async def view_history(uuid: str, session: AsyncSession, device_uuid: str,
                       type_research_uuid: str, date_from: str, date_to: str,
                       patient_uuid: str, research_uuid_part: str):

    """
    Просмотр DesyncDatas данных по uuid пользователя с возможностью поиска по части UUID исследования.
    :param uuid: str uuid пользователя
    :param session: AsyncSession сессия
    :param device_uuid: str uuid устройства
    :param type_research_uuid: str uuid типа исследования
    :param date_from: str дата с которой начать поиск
    :param date_to: str дата до которой искать
    :param patient_uuid: str uuid пациента
    :param research_uuid_part: str часть uuid исследования для поиска
    :return: model
    """
    query_result = select(DesyncDatas).where(
        or_(uuid is None, DesyncDatas.user_uuid == uuid),
        or_(device_uuid is None, DesyncDatas.device_uuid == device_uuid),
        or_(type_research_uuid is None, DesyncDatas.type_research_uuid == type_research_uuid),
        or_(patient_uuid is None, DesyncDatas.patient_uuid == patient_uuid),
        (date_from is None or DesyncDatas.date >= DT.datetime.strptime(f"{date_from} 00:00:00", '%Y%m%d %H:%M:%S')),
        (date_to is None or DesyncDatas.date <= DT.datetime.strptime(f"{date_to} 23:59:59", '%Y%m%d %H:%M:%S')),
        (research_uuid_part is None or text(f"DesyncDatas.uuid::text LIKE '%{research_uuid_part}%'"))
    )
    try:
        data = await session.execute(query_result)
        result = data.scalars().all()
        return result, None
    except (exc.SQLAlchemyError, RequestException, socket.gaierror) as e:
        print(f"LOG: {e}")
        return None, e
    finally:
        await session.close()


async def create_research(data: DesyncDatasCreate, duration: int,
                          session: AsyncSession):
    """
    Создать исследование по модели. Передача данных в RethinkDB и PostgreSQL
    :param data: DesyncDatasCreate модель
    :param duration: длительность секунд исследования
    :param session: AsyncSession
    :return: DesyncDatas
    """
    result = DesyncDatas.from_orm(data)

    try:
        with get_rethink_session() as conn:
            active_research = r.db(db).table(table).filter(
                (r.row["device_uuid"] == str(result.device_uuid)) &
                ((r.row["research_status"] == "open") | (r.row["research_status"] == "in_process"))
            ).run(conn)

            active_research_list = list(active_research)
            if active_research_list:
                return None, 1

        patient = await session.get(Patient, result.patient_uuid)
        async with session:
            session.add(result)
            await session.commit()
            await session.refresh(result)
        with get_rethink_session() as conn:
            r.db(db).table(table).filter(r.row["device_uuid"] ==
                                         str(result.device_uuid)).update({
                                             "patient_code": patient.code,
                                             "desync_data_uuid": str(result.uuid),
                                             "research_status": "open",
                                             "duration": duration
                                         }).run(conn)
        return result, 0
    except (HTTPException, RequestException, socket.gaierror, exc.SQLAlchemyError) as e:
        print(f"LOG: {e}")
        return None, e
    finally:
        await session.close()


async def get_data_from_rethink(request: Request, filter_status: str = None) -> Iterator[str]:
    client_ip = request.client.host
    print(f"Client {client_ip} connected")

    with get_rethink_session() as conn:
        # Определяем условие фильтрации в зависимости от filter_status
        if filter_status in ["open", "in_process"]:
            filter_conditions = {"research_status": filter_status}
        else:
            filter_conditions = (r.row["research_status"] == "in_process") | (r.row["research_status"] == "open")

        # Проверяем, есть ли данные по заданному фильтру
        if r.db("RTDB_desync").table("dev_desync").filter(filter_conditions).is_empty().run(conn):
            return

        try:
            while True:
                device_status = r.db("RTDB_desync").table("dev_desync").filter(filter_conditions).pluck(
                    'impedance', 'channel_desync', 'device', 'patient_code').run(conn)

                for document in device_status:
                    json_data = json.dumps({
                        "impedance": document['impedance'],
                        "channel_desync": document['channel_desync'],
                        "device": document['device'],
                        "patient_code": document['patient_code']
                    })
                    yield f"data:{json_data}\n\n"
                    await asyncio.sleep(3)

        except asyncio.CancelledError as e:
            print(f"Disconnected from client (via refresh/close) {client_ip}")
            raise e


async def get_data_from_rethink_by_type_research_uuid(request: Request, desync_data_uuid: UUID,
                                                      filter_status: str = None) -> Iterator[str]:
    client_ip = request.client.host
    print(f"Client {client_ip} connected")

    with get_rethink_session() as conn:
        if filter_status in ["open", "in_process"]:
            filter_conditions = ((r.row["research_status"] == filter_status) & (
                        r.row["desync_data_uuid"] == str(desync_data_uuid)))
        else:
            filter_conditions = ((r.row["research_status"] == "in_process") | (r.row["research_status"] == "open")) & (
                    r.row["desync_data_uuid"] == str(desync_data_uuid))

        if r.db("RTDB_desync").table("dev_desync").filter(filter_conditions).is_empty().run(conn):
            return

        try:
            while True:
                device_status = r.db("RTDB_desync").table("dev_desync").filter(filter_conditions).pluck(
                    'impedance', 'channel_desync', 'device', 'patient_code').run(conn)

                for document in device_status:
                    json_data = json.dumps({
                        "impedance": document['impedance'],
                        "channel_desync": document['channel_desync'],
                        "device": document['device'],
                        "patient_code": document['patient_code']
                    })
                    yield f"data:{json_data}\n\n"
                    await asyncio.sleep(3)

        except asyncio.CancelledError as e:
            print(f"Disconnected from client (via refresh/close) {client_ip}")
            raise e

# async def get_research_with_status( session: AsyncSession):
#     """
#     Получить данные исследований по определенным статусам из RethinkDB и получить соответствующие записи из PostgreSQL.
#     :param session: Сессия PostgreSQL для выполнения запроса.
#     :return: Список объектов DesyncDatas или None в случае ошибки.
#     """
#     try:
#         # Здесь добавляем контекстный менеджер для соединения с RethinkDB
#         with get_rethink_session() as conn:
#             # Извлечение UUID для статусов 'open' и 'in_process'
#             research_status = r.db("RTDB_desync").table("dev_desync"). \
#                 filter(lambda doc: (doc.has_fields('research_status') & (
#                         doc['research_status'].eq("in_process") | doc['research_status'].eq("open"))) & doc.has_fields(
#                 'desync_data_uuid')). \
#                 pluck('desync_data_uuid').run(conn)
#
#             uuids = [status['desync_data_uuid'] for status in research_status if 'desync_data_uuid' in status]
#
#             if uuids:
#                 result = await session.execute(select(DesyncDatas).where(DesyncDatas.uuid.in_(uuids)))
#                 desync_data_list = result.scalars().all()
#                 return desync_data_list
#             return []
#     except (exc.SQLAlchemyError, Exception) as e:
#         print(f"Database error: {e}")
#         return None
#     finally:
#         await session.close()
