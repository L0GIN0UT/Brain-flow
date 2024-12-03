import os
from dotenv import load_dotenv, set_key
from models.settings import SettingsReed, SettingsUpdate
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


def read_settings():
    try:
        settings = {
            "BORDER_TIME": os.getenv("BORDER_TIME"),
            "FIVE_MINUTE_SAMPLE": os.getenv("FIVE_MINUTE_SAMPLE"),
            "USE_IMPEDANCE": os.getenv("USE_IMPEDANCE"),
            "MAX_SAMPLES": os.getenv("MAX_SAMPLES"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL"),
            "MAIL_ADDRESS": os.getenv("MAIL_ADDRESS"),
            "MAIL_SMTP_SERVER": os.getenv("MAIL_SMTP_SERVER"),
            "MAIL_PORT": os.getenv("MAIL_PORT"),
            "MAIL_MESSAGE_SUBJECT": os.getenv("MAIL_MESSAGE_SUBJECT"),
            "MAIL_MESSAGE_TEXT": os.getenv("MAIL_MESSAGE_TEXT"),
        }
        return settings, None
    except Exception as e:
        return None, str(e)


def reload_env():
    load_dotenv(dotenv_path=env_path, override=True)


def update_admin_email(new_email: str):
    try:
        set_key(env_path, "ADMIN_EMAIL", new_email)
        reload_env()
        return None
    except Exception as e:
        return str(e)


async def update_settings(settings_update: SettingsUpdate):
    try:
        env_vars = {
            "BORDER_TIME": str(settings_update.border_time) if settings_update.border_time is not None else None,
            "FIVE_MINUTE_SAMPLE": str(
                settings_update.five_minute_sample) if settings_update.five_minute_sample is not None else None,
            "USE_IMPEDANCE": str(settings_update.use_impedance) if settings_update.use_impedance is not None else None,
            "MAX_SAMPLES": str(settings_update.max_samples) if settings_update.max_samples is not None else None,
            "LOG_LEVEL": settings_update.log_level if settings_update.log_level is not None else None,
            "MAIL_ADDRESS": settings_update.mail_address if settings_update.mail_address is not None else None,
            "MAIL_PASSWORD": settings_update.mail_password if settings_update.mail_password is not None else None,
            "MAIL_SMTP_SERVER": settings_update.mail_smtp_server if settings_update.mail_smtp_server is not None else None,
            "MAIL_PORT": settings_update.mail_port if settings_update.mail_port is not None else None,
            "MAIL_MESSAGE_SUBJECT": settings_update.mail_message_subject if settings_update.mail_message_subject is not None else None,
            "MAIL_MESSAGE_TEXT": settings_update.mail_message_text if settings_update.mail_message_text is not None else None,
        }

        for key, value in env_vars.items():
            if value is not None:
                if isinstance(value, int):
                    set_key(env_path, key, str(value))
                else:
                    set_key(env_path, key, value)

        reload_env()

        updated_settings, err = read_settings()
        if err:
            return None, err

        return updated_settings, None
    except Exception as e:
        return None, str(e)
