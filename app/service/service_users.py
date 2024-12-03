import hashlib
import json
import random
import string
import socket
import uuid
from datetime import datetime, timedelta, timezone
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from http import HTTPStatus
from typing import List, Any, Tuple
from uuid import UUID
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from requests import RequestException
from sqlalchemy import select, exc, or_
from jose import JWTError, jwt
from sqlalchemy.sql.operators import ilike_op

from db.postgres import get_session, AsyncSession
from models.user import UserAuthorization, User, UserRecoveryPassword
from service.common import update_model_in_database, get_model_details, get_models_list
from config.settings import settings
from redis_module.redis_client import redis


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/authorization")


async def write_user_to_database(model_to_write, session: AsyncSession = Depends(get_session)):
    """
    Добавить пользователя в базу данных, предварительно хэшировав пароль
    :param model_to_write: модель для добавления
    :param session: сессия базы данных
    :return: model модель, записанная в базу данных
    """

    salt = get_random_string()
    hashed_password = hash_password(model_to_write.password, salt)
    model_to_write.password = f"{salt}${hashed_password}"

    try:
        session.add(model_to_write)
        await session.commit()
        await session.refresh(model_to_write)
        return model_to_write, None
    except (exc.SQLAlchemyError, RequestException, socket.gaierror) as e:
        print(f"LOG: {e}")
        return None, e
    finally:
        await session.close()


async def authorization(email: str, password: str,
                        session: AsyncSession = Depends(get_session)) -> User:
    """
    Проверить существует ли пользователь с текущим паролем и логином,
    возвращает модель пользователя если такой существует
    :param email: почта пользователя
    :param password: пароль пользователя
    :param session: сессия базы данных
    :return: User авторизованная модель
    """
    try:
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        result_out = result.scalars().first()
        if not result_out or not validate_password(password=password, hashed_password=result_out.password):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        return result_out
    except (exc.SQLAlchemyError, RequestException) as e:
        print(f"LOG: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")  # Бросаем исключение
    except socket.gaierror as e:
        print(f"LOG: {e} - скорее всего легла БД")
        raise HTTPException(status_code=500, detail="Database connection error")  # Бросаем исключение
    finally:
        await session.close()


async def recovery_password(user_recovery_password_model: UserRecoveryPassword,
                            session: AsyncSession = Depends(get_session)) -> UserAuthorization:
    """
    Создаёт новый пароль пользователю и перезаписывает его в базе данных
    :param user_recovery_password_model: данные с логином пользователя
    :param session: сессия базы данных
    :return: UserAuthorization: модель User с не хэшированным паролем
    """
    try:
        stmt = select(User).where(User.email == user_recovery_password_model.email)
        result = await session.execute(stmt)
        result_model = result.scalars().first()
        if not result_model:
            raise HTTPException(status_code=400, detail="Incorrect email")

        rand_password = generate_password(6)
        salt = get_random_string()
        hashed_password = hash_password(rand_password, salt)
        result_model.password = f"{salt}${hashed_password}"

        await session.commit()

        return_model = UserAuthorization(
            email=result_model.email,
            password=rand_password
        )
        email_result = send_email_to_user(return_model.password, return_model.email)

        return (return_model, None) if email_result else (None, HTTPStatus.BAD_REQUEST)
    except (exc.SQLAlchemyError, RequestException, socket.gaierror) as e:
        print(f"LOG: {e}")
        return None, e
    finally:
        await session.close()


def get_random_string(length=12):
    """ Генерирует случайную строку, использующуюся как соль """
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def hash_password(password: str, salt: str = None):
    """ Хеширует пароль с солью """
    if salt is None:
        salt = get_random_string()
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return enc.hex()


def validate_password(password: str, hashed_password: str):
    """ Проверяет, что хеш пароля совпадает с хешем из БД """
    salt, hashed = hashed_password.split("$")
    return hash_password(password, salt) == hashed


def generate_password(length):
    """ Создаёт пароль из случайного набора букв и цифр """
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Создание токена по переданным в data данным.
    :param data: данные, которые будут в токене
    :param expires_delta: время жизни токена
    :return: str: строка токена, в которой хранятся данные из data
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    # Генерируем уникальный session_id и добавляем его в токен
    session_id = str(uuid.uuid4())
    to_encode.update({"session_id": session_id})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, session_id


async def get_current_uuid_from_token(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Получение uuid пользователя из токена и проверка сессии.
    :param token: токен, в котором хранятся данные
    :return: dict: словарь с uuid пользователя и флагом is_admin
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Декодируем токен и извлекаем данные
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uuid: str = payload.get("sub")
        is_admin: bool = payload.get("admin", False)
        token_session_id: str = payload.get("session_id")

        if uuid is None or token_session_id is None:
            raise credentials_exception

        # Получаем session_id из Redis
        session_id = await redis.get(f"user_session:{uuid}")
        if session_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Сессия истекла или недействительна")

        # Проверяем, соответствует ли session_id из токена сохраненному в Redis
        if session_id != token_session_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Несоответствие идентификатора сессии")

        # Получаем токен из Redis и сравниваем его с предоставленным токеном
        saved_token = await redis.get(f"user_token:{uuid}")
        if saved_token is None or saved_token != token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительная сессия")

        return {"uuid": uuid, "is_admin": is_admin}

    except JWTError:
        raise credentials_exception


async def get_current_user_uuid(
    token: str = Depends(oauth2_scheme)
) -> str:
    uuid_data = await get_current_uuid_from_token(token)
    return uuid_data['uuid']


async def check_admin_status(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not access",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uuid: str = payload.get("sub")
        token_session_id: str = payload.get("session_id")

        if uuid is None or token_session_id is None:
            raise credentials_exception

        # Проверяем сессию
        session_id = await redis.get(f"user_session:{uuid}")
        if session_id is None or session_id != token_session_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Сессия истекла или недействительна")

        # Проверяем токен
        saved_token = await redis.get(f"user_token:{uuid}")
        if saved_token is None or saved_token != token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительная сессия")

        user, err = await get_model_details(model_uuid=UUID(uuid), model_type=User, session=session)
        if err:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
        if user.email == settings.admin_email:
            return uuid
        else:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    except AttributeError as e:
        print(f"LOG: {e} - скорее всего БД легла")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


def send_email_to_user(new_password: str, user_mail: str):
    sender_email = settings.mail_address
    receiver_email = user_mail
    password = settings.mail_password
    smtp_server = settings.mail_smtp_server
    port = settings.mail_port # Порт для TLS

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = settings.mail_message_subject

    text = f"""
        <html>
        <head>
            <style>
                body {{
                    background-color: #0D1B2A;
                    color: #FFFFFF;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                }}
                .content {{
                    background-color: #1B263B;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
                    display: inline-block;
                }}
                .password {{
                    font-size: 50px;
                    font-weight: bold;
                    color: #4CAF50;
                    margin-bottom: 20px;
                }}
                .message-text {{
                    font-size: 20px;
                    color: #FFFFFF;
                }}
            </style>
        </head>
        <body>
            <div class="content">
                <p class="password">{new_password}</p>
                <p class="message-text">{settings.mail_message_text}</p>
            </div>
        </body>
        </html>
        """

    message.attach(MIMEText(text, "html"))

    try:
        # Используем smtplib.SMTP для подключения к порту 587
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Проверка соединения с сервером
        server.starttls()  # Включаем TLS
        server.ehlo()  # Проверка соединения с сервером снова после включения TLS
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        return True
    except smtplib.SMTPException as e:
        print(f"Произошла ошибка SMTP: {e}")
        return False
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return False


async def search_user(name_or_surname: str, session: AsyncSession) -> list[Any] | tuple[Any, None] | tuple[
    None, Any] | Any:
    """
    Поиск пользователя по имени или фамилии.
    :param name_or_surname: фамилия или имя пользователя
    :param session: сессия бд
    :return: list: найденные пользователи
    """
    try:
        query = select(User).filter(
            or_(ilike_op(User.first_name, f"{name_or_surname}%"), ilike_op(User.last_name, f"{name_or_surname}%")))
        if name_or_surname is None:
            user, err = await get_models_list(User, session=session)
            if err:
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err)
            elif not user:
                return [], None
            return user, None
        result = await session.execute(query)
        return result.scalars().all(), None
    except (exc.SQLAlchemyError, RequestException, socket.gaierror) as e:
        print(f"LOG: {e}")
        return None, e
    finally:
        await session.close()
