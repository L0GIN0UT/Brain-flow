import uuid
from datetime import timedelta
from http import HTTPStatus
import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from db.postgres import get_session, AsyncSession
from models.token import Token
from service import service_users
from config.settings import settings
from service.service_settings import reload_env
from config.logs_config import logger_app_login
from redis_module.redis_client import redis

router = APIRouter(
    prefix='/api/v1/login',
    tags=['Раздел Логин']
)

ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


@router.post(
    '/authorization',
    summary="Авторизация пользователя",
    description="Авторизация пользователя в системе",
    response_description="Данные о токене доступа"
)
async def authorization_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_session)
) -> Token:
    try:
        reload_env()
        user = await service_users.authorization(email=form_data.username, password=form_data.password, session=session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )

        is_admin = user.email == settings.admin_email
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token, session_id = service_users.create_access_token(
            data={"sub": str(user.uuid), "admin": is_admin},
            expires_delta=access_token_expires
        )

        # Удаляем старую сессию (если есть)
        previous_session = await redis.get(f"user_session:{user.uuid}")
        if previous_session:
            await redis.delete(f"user_token:{user.uuid}")
            await redis.delete(f"user_session:{user.uuid}")

        # Сохраняем новые данные сессии
        await redis.set(f"user_token:{user.uuid}", access_token, ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        await redis.set(f"user_session:{user.uuid}", session_id, ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    except Exception as err:
        logger_app_login.error(f"ERROR: {err}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")

    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/test_auth",
    summary="Проверка аутентификации пользователя",
    description="Получение информации о текущем пользователе из токена",
    response_description="UUID пользователя и статус администратора"
)
async def sample_endpoint(user_data: dict = Depends(service_users.get_current_uuid_from_token)):
    return {"user_uuid": user_data["uuid"], "is_admin": user_data["is_admin"]}