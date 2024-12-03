import io
import os
import socket
import uuid
from datetime import datetime
from typing import Tuple, Any
from uuid import UUID

from http import HTTPStatus

from PIL import Image
from fastapi import HTTPException, Depends, UploadFile
from redis import Redis
from requests import RequestException
from sqlalchemy.future import select
from sqlalchemy import exc, delete

from db.postgres import get_session, AsyncSession
from models.clinicaddress import ClinicAddress

from models.clinic import Clinic
from service import service_settings
from models.user import User
from config.settings import settings
import json

redis_client = Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)


async def cache_data(key: str, value: Any, expire: int = settings.redis_cache_expire):
    await redis_client.setex(key, expire, json.dumps(value, default=str))


async def get_cached_data(key: str) -> Any | None:
    cached_data = redis_client.get(key)
    if cached_data:
        return json.loads(cached_data)
    return None


def custom_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

async def write_model_to_database(model_to_write, model_type, session: AsyncSession = Depends(get_session)):
    """
    Добавить модель с помощью типа модели в базу данных
    :param model_to_write: модель для добавления
    :param model_type: тип модели
    :param session:
    :return: list[model]
    """
    result = model_type.from_orm(model_to_write)
    try:
        session.add(result)
        await session.commit()
        await session.refresh(result)
        return result, None
    except (exc.SQLAlchemyError, RequestException, socket.gaierror) as e:
        print(f"LOG: {e}")
        return None, e
    finally:
        await session.close()


async def get_models_list(models_type, session: AsyncSession = Depends(get_session)):
    """
    Получить список моделей по типу моделей из базы данных
    :param models_type: тип моделей
    :param session:
    :return: list[model]
    """
    # model_list = None
    try:
        result = await session.execute(select(models_type))
        model_list = result.scalars().all()
        return model_list, None
    except (exc.SQLAlchemyError, RequestException, socket.gaierror) as e:
        print(f"LOG: {e}")
        return None, e
    finally:
        await session.close()


async def get_model_details(model_uuid: UUID, model_type, session: AsyncSession):
    """
    Получить модель по uuid и типу из базы данных
    :param model_uuid: uuid модели
    :param model_type: тип модели
    :param session: сессия
    :return: model
    """
    try:
        result = await session.get(model_type, model_uuid)
        return result, None
    except (HTTPException, RequestException, socket.gaierror) as e:
        print(f"LOG: {e}")
        return None, e


async def update_model_in_database(model_uuid: UUID, model_type, model_to_update,
                                   session: AsyncSession = Depends(get_session)):
    """
    Изменяет параметры выбранной модели в базе данных
    :param model_uuid: uuid модели
    :param model_type: тип модели
    :param model_to_update: модель, которую нужно записать в бд
    :param session:
    :return: model
    """
    model, err = await get_model_details(model_uuid, model_type, session=session)
    if err:
        return None, err
    if model:
        model_data = model_to_update.dict(exclude_unset=True)
        admin_email_changed = False
        for key, value in model_data.items():
            if key == "password" and not value:
                continue
            if key == "email":
                if model_type is User and model.email == os.getenv("ADMIN_EMAIL"):
                    admin_email_changed = True
                    new_admin_email = value
            setattr(model, key, value)
        try:
            session.add(model)
            await session.commit()
            await session.refresh(model)
            if admin_email_changed:
                err = service_settings.update_admin_email(new_admin_email)
                if err:
                    print(f"Error updating admin email in .env: {err}")
                else:
                    print(f"Admin email updated to: {new_admin_email}")
                service_settings.reload_env()
        except (exc.SQLAlchemyError, RequestException, socket.gaierror) as e:
            print(f"LOG: {e}")
            return None, e
        finally:
            await session.close()
    return model, None


async def delete_model_clinic(clinic_uuid: UUID, session: AsyncSession = Depends(get_session)) -> None:
    """
    Удалить клинику и связанные адреса по uuid из базы данных
    :param clinic_uuid: uuid клиники
    :param session: AsyncSession
    :return: None
    """
    try:
        # Удаление всех связанных записей в ClinicAddress
        await session.execute(delete(ClinicAddress).where(ClinicAddress.clinic_uuid == clinic_uuid))

        # Получение клиники для удаления
        clinic = await session.get(Clinic, clinic_uuid)
        if clinic:
            await session.delete(clinic)
            await session.commit()
        else:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Нет такой клиники")
    except exc.SQLAlchemyError as e:
        await session.rollback()  # Откат транзакции при ошибке
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=f'Ошибка удаления клиники - {e.args[0]}')


async def delete_model_to_database(model_uuid: UUID, model_type,
                                   session: AsyncSession = Depends(get_session)):
    """
    Удалить модель по uuid и типу из базы данных
    :param model_uuid: uuid модели
    :param model_type: тип модели
    :param session: AsyncSession
    :return: model
    """
    model, err = await get_model_details(model_uuid, model_type, session=session)
    if err:
        return None, err
    if model:
        try:
            await session.delete(model)
            await session.commit()
        except (exc.SQLAlchemyError, RequestException, socket.gaierror) as e:
            print(f"LOG: {e}")
            return None, e
        finally:
            await session.close()
    return model, None


async def get_admin_panel_list(session: AsyncSession, clinic, users, type_research, device_types):
    clinic_list, err = await get_models_list(models_type=clinic, session=session)
    if err:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err)
    elif not clinic_list:
        return [], None
    current_clinic = clinic_list[0]

    users_list, err = await get_models_list(models_type=users, session=session)
    if err:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err)
    elif not users_list:
        return [], None

    device_types_list, err = await get_models_list(models_type=device_types, session=session)
    if err:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err)
    elif not device_types_list:
        return [], None

    type_research_list, err = await get_models_list(models_type=type_research, session=session)
    if err:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err)
    elif not type_research_list:
        return [], None

    return {'clinic_name': current_clinic.name, 'clinic_logo': current_clinic.logo, 'user': users_list,
            'device_types': device_types_list, 'type_research': type_research_list}, None


async def search(model, filter_model, session: AsyncSession) -> tuple[Any, None] | tuple[None, Any]:
    try:
        query = filter_model.filter(select(model))
        result = await session.execute(query)
        return result.scalars().all(), None
    except (exc.SQLAlchemyError, RequestException, socket.gaierror) as e:
        print(f"LOG: {e}")
        return None, e
    finally:
        await session.close()


async def upload_image(model, uuid: UUID, filename: str, session: AsyncSession = Depends(get_session)):
    try:
        result = await session.get(model, uuid)
        if model is Clinic:
            result.logo = filename
            result, err = await update_model_in_database(uuid, model, result, session)
            if err:
                print(f"LOG: {err}")
                return None, err
            return result.logo, None
        else:
            result.avatar = filename
            result, err = await update_model_in_database(uuid, model, result, session)
            if err:
                print(f"LOG: {err}")
                return None, err
            return result.avatar, None
    except (HTTPException, RequestException, socket.gaierror) as e:
        print(f"LOG: {e}")
        return None, e
    finally:
        await session.close()


async def download_image(model, uuid: UUID, session: AsyncSession = Depends(get_session)):
    try:
        if model is Clinic:
            result = await session.get(model, uuid)
            return result.logo, None
        else:
            result = await session.get(model, uuid)
            return result.avatar, None
    except (HTTPException, RequestException, socket.gaierror) as e:
        print(f"LOG: {e}")
        return None, e
    finally:
        await session.close()


async def get_clinic_uuid(session: AsyncSession = Depends(get_session)):
    clinics, err = await get_models_list(Clinic, session=session)
    if err:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err)
    elif not clinics:
        return []
    return clinics[0].uuid


async def compress_image(image_file: UploadFile, max_size_mb: float = 0.5) -> Tuple[io.BytesIO, str | None, str]:
    try:
        image = Image.open(image_file.file)

        # Проверяем режим изображения и конвертируем в RGB при необходимости
        if image.mode in ("RGBA", "LA", "P", "L"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode in ("RGBA", "LA"):
                # Для изображений с альфа-каналом используем его как маску
                background.paste(image.convert("RGBA"), mask=image.convert("RGBA").split()[3])
            else:
                # Для изображений без альфа-канала просто конвертируем
                background.paste(image)
            image = background
        else:
            image = image.convert("RGB")

        output_io_stream = io.BytesIO()
        image.save(output_io_stream, format='JPEG', quality=85)
        output_io_stream.seek(0)
        if output_io_stream.getbuffer().nbytes > 2 * 1024 * 1024:
            return None, None, "Размер сжатого изображения превышает 2 MB"
        unique_filename = f"{uuid.uuid4()}.jpg"

        return output_io_stream, unique_filename, None
    except Exception as e:
        return None, None, str(e)


def validate_uuid(uuid_str: str | None) -> str | None:
    """
    Функция для проверки валидности UUID.
    Если UUID валиден, возвращаем его, иначе возвращаем None.
    :param uuid_str: str
    :return: str | None
    """
    if uuid_str:
        try:
            return str(UUID(uuid_str, version=4))
        except ValueError:
            return None
    return None