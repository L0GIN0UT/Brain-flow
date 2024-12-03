import time
from http import HTTPStatus
from typing import Tuple, List, Any
from uuid import UUID
import socket
from datetime import datetime

from fastapi import HTTPException
from requests import RequestException
from sqlalchemy import select, exc
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.future import select
from rethinkdb import r, errors as re

from config.settings import settings
from db.rethink import get_rethink_session
from db.postgres import AsyncSession
from models.device import Device, DeviceCreate, DeviceUpdate, DeviceFilter
from models.device_type import DeviceType, DeviceDeviceTypeLink
from service.common import get_model_details

db = settings.rethinkdb_db
table = settings.rethinkdb_table


async def create_device(clinic_uuid: UUID, data: DeviceCreate, session: AsyncSession) -> Device:
    """
    Создать устройство по модели. Передача данных в RethinkDB и PostgreSQL
    :param clinic_uuid: uuid клиники
    :param data: DeviceCreate модель
    :param session: AsyncSession
    :return: Device
    """
    result = Device.from_orm(data)
    result.clinic_uuid = clinic_uuid

    for device_type_uuid in data.device_types:
        device_type, err = await get_model_details(model_uuid=device_type_uuid, model_type=DeviceType, session=session)
        if err:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
        if device_type:
            result.device_types.append(device_type)
    try:
        session.add(result)
        await session.commit()
        await session.refresh(result)
        with get_rethink_session() as conn:
            r.db(db).table(table).insert({"device": result.name, "device_uuid": str(result.uuid), "status": False,
                                          "calibration": False, "time_calibration": 10.0, "baseline": {},
                                          "channel_desync": {}, "impedance": {}, "desync_data_uuid": {}, "research_status": {},
                                          "patient_code": {}, "date_start": {}, "duration": {}}).run(conn)
        return result, None
    except (exc.SQLAlchemyError, RequestException, socket.gaierror) as e:
        print(f"LOG: {e}")
        return None, e
    finally:
        await session.close()


async def get_all(session: AsyncSession) -> tuple[Any, None] | tuple[None, Any]:
    """
    Получить список устройств
    :param session: AsyncSession
    :return: list[Device] модель
    """
    try:
        result = await session.execute(select(Device))
        devices = result.scalars().all()
        return devices, None
    except (exc.SQLAlchemyError, RequestException, socket.gaierror) as e:
        print(f"LOG: {e}")
        return None, e
    finally:
        await session.close()


async def read_device(uuid, session: AsyncSession) -> Device | None:
    """
    Получить устройство
    :param uuid: uuid
    :param session: AsyncSession
    :return: DeviceRead
    """
    try:
        result = await session.get(Device, uuid)
        return result
    except (exc.SQLAlchemyError, RequestException, socket.gaierror) as e:
        print(f"LOG: {e}")
        return None


async def update_device(uuid, session: AsyncSession, data: DeviceUpdate | list[tuple]):
    """
    Обновить данные об устройстве. Передача данных в PostgreSQL
    :param uuid: uuid
    :param session: AsyncSession
    :param data: DeviceUpdate | list[tuple]
    :return: DeviceRead
    """
    device = await read_device(uuid, session=session)
    if device:
        device_data = data.dict(exclude_unset=True)
        for key, value in device_data.items():
            if key == "device_types" and isinstance(value, list):
                device.device_types.clear()
                for device_type_uuid in value:
                    device_type, err = await get_model_details(model_uuid=device_type_uuid, model_type=DeviceType, session=session)
                    if err:
                        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
                    if device_type:
                        if session.is_active:
                            session.expunge(device_type)  # Проверка наличия объекта в сессии перед удалением
                        device.device_types.append(device_type)
                continue
            setattr(device, key, value)
        try:
            session.add(device)
            await session.commit()
            await session.refresh(device)
        except (exc.SQLAlchemyError, RequestException, socket.gaierror) as e:
            print(f"LOG: {e}")
            return None, e
    return device, None


async def delete_device(uuid, session: AsyncSession):
    """
    Удалить устройство. Передача данных в RethinkDB и PostgreSQL
    :param uuid: uuid
    :param session: AsyncSession
    :return: DeviceRead
    """
    device = await read_device(uuid, session=session)
    if device:
        try:
            await session.delete(device)
            await session.commit()
            with get_rethink_session() as conn:
                r.db(db).table(table).filter({"device_uuid": str(uuid)}).delete().run(conn)
        except (exc.SQLAlchemyError, RequestException, socket.gaierror) as e:
            print(f"LOG: {e}")
            return None, e
        finally:
            await session.close()
    return device, None


# сделать синхронную функцию
async def start_stop_process(uuid: UUID, status: bool, session: AsyncSession):
    """
    Запуск и остановка устройства. Передача данных в RethinkDB
    :param uuid: uuid
    :param status: bool
    :param session: AsyncSession
    :return: DeviceRead
    """
    device = await read_device(uuid=uuid, session=session)
    if device:
        try:
            device.status = status
            session.add(device)
            await session.commit()
            await session.refresh(device)

            with get_rethink_session() as conn:
                r.db(settings.rethinkdb_db).table(settings.rethinkdb_table).filter(
                    {"device_uuid": str(uuid)}
                ).update({"status": status}).run(conn)

            return device, None
        except (re.ReqlError, RequestException, socket.gaierror) as e:
            print(f"LOG: {e}")
            return None, e
        finally:
            await session.close()
    return None, None


async def calibration_device(uuid: UUID, calibration: bool, calibration_time: float, session: AsyncSession):
    """
    Калибровка устройства. Передача данных в RethinkDB
    :param uuid: uuid
    :param status: bool
    :param session: AsyncSession
    :return: DeviceRead
    """
    device = await read_device(uuid=uuid, session=session)
    if device:
        try:
            with get_rethink_session() as conn:
                r.db(db).table(table).filter({"device_uuid": str(device.uuid)}).update(
                    {"calibration": calibration, "time_calibration": calibration_time,
                     "date_start": datetime.now(r.make_timezone('04:00'))}).run(conn)
            return device
        except (re.ReqlError, RequestException, socket.gaierror) as e:
            print(f"LOG: {e}")
            return None
        finally:
            await session.close()
    return device


def get_rethink_session_temp() -> r:
    """подключении к RT_DB для теста и дебага api"""
    conn = r.connect('localhost', '28015')
    return conn


async def devices_status():
    """
    Возвращает имя устройства и его состояние. Передача данных из RethinkDB
    """
    try:
        with get_rethink_session() as conn:
            device_status = r.db(db).table(table).pluck('device', 'status').run(conn)
        return device_status, None
    except (re.ReqlError, RequestException, socket.gaierror) as e:
        print(f"LOG: {e}")
        return None, e


async def get_device(uuid, session: AsyncSession) -> Device | None:
    """
    Получить устройство
    :param uuid: uuid
    :param session: AsyncSession
    :return: DeviceRead
    """
    try:
        result = await session.execute(
            select(Device).options(selectinload(Device.device_types)).where(Device.uuid == uuid)
        )
        device = result.scalar_one_or_none()
        if device:
            with get_rethink_session() as conn:
                status = r.db(db).table(table).filter(r.row['device_uuid'] == str(uuid)).get_field('status').run(conn)
                for s in status:
                    device.status = s
        return device, None
    except (exc.SQLAlchemyError, RequestException, socket.gaierror) as e:
        print(f"LOG: {e}")
        return None, e
    finally:
        await session.close()


async def filter_status(status):
    if status:
        try:
            with get_rethink_session() as conn:
                device = r.db(db).table(table).filter(r.row["status"] == status).pluck('device', 'status').run(conn)
            return device
        except (re.ReqlError, RequestException, socket.gaierror) as e:
            print(f"LOG: {e}")
            return None
    else:
        return None


async def get_devices_filter(device_filter: DeviceFilter, session: AsyncSession) -> Tuple[List[Any], None] | Tuple[None, Any]:
    try:
        query = select(Device).options(joinedload(Device.device_types))
        query = device_filter.filter(query)
        result = await session.execute(query)
        devices = result.scalars().unique().all()

        # Проверяем наличие фильтра по device_type
        if hasattr(device_filter, 'device_type') and device_filter.device_type:
            if device_filter.device_type.name:
                devices = [device for device in devices if
                           any(dt.name == device_filter.device_type.name for dt in device.device_types)]
            if device_filter.device_type.name__like:
                devices = [device for device in devices if
                           any(device_filter.device_type.name__like in dt.name for dt in device.device_types)]

        devices_with_types = []
        for device in devices:
            device_dict = device.dict()

            with get_rethink_session() as conn:
                status = r.db(db).table(table).filter(r.row['device_uuid'] == str(device.uuid)).get_field('status').run(
                    conn)
                for s in status:
                    device_dict["status"] = s

            device_dict["device_types"] = [
                {
                    "name": dt.name,
                    "description": dt.description,
                    "uuid": dt.uuid
                }
                for dt in device.device_types
            ]
            devices_with_types.append(device_dict)

        return devices_with_types, None
    except (AssertionError, RequestException, socket.gaierror) as e:
        print(f"LOGS: {e}")
        return None, e
    finally:
        await session.close()


def check_status_device(device_uuid: UUID) -> bool | Exception:
    time.sleep(1)
    try:
        with get_rethink_session() as conn:
            status_rethink = r.db(settings.rethinkdb_db).table(settings.rethinkdb_table).filter(
                {"device_uuid": str(device_uuid)}).pluck("status").run(conn)
            for _ in status_rethink:
                status_rethink = _["status"]
                return status_rethink
    except re.ReqlError as e:
        return HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f'On/Off device error - {e.args[0]}')
