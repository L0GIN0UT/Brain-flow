from pydantic import BaseModel, Field


class SettingsReed(BaseModel):
    border_time: int = Field(None, alias="BORDER_TIME")
    five_minutes_sample: int = Field(None, alias="FIVE_MINUTE_SAMPLE")
    use_impedance: int = Field(None, alias="USE_IMPEDANCE")
    max_samples: int = Field(None, alias="MAX_SAMPLES")
    log_level: str = Field(None, alias="LOG_LEVEL")
    mail_address: str = Field(None, alias="MAIL_ADDRESS")
    mail_smtp_server: str = Field(None, alias="MAIL_SMTP_SERVER")
    mail_port: str = Field(None, alias="MAIL_PORT")
    mail_message_subject: str = Field(None, alias="MAIL_MESSAGE_SUBJECT")
    mail_message_text: str = Field(None, alias="MAIL_MESSAGE_TEXT")


class SettingsUpdate(BaseModel):
    border_time: int = Field(None, alias="BORDER_TIME")
    five_minute_sample: int = Field(None, alias="FIVE_MINUTE_SAMPLE")
    use_impedance: int = Field(None, alias="USE_IMPEDANCE")
    max_samples: int = Field(None, alias="MAX_SAMPLES")
    log_level: str = Field(None, alias="LOG_LEVEL")
    mail_address: str = Field(None, alias="MAIL_ADDRESS")
    mail_password: str = Field(None, alias="MAIL_PASSWORD")
    mail_smtp_server: str = Field(None, alias="MAIL_SMTP_SERVER")
    mail_port: str = Field(None, alias="MAIL_PORT")
    mail_message_subject: str = Field(None, alias="MAIL_MESSAGE_SUBJECT")
    mail_message_text: str = Field(None, alias="MAIL_MESSAGE_TEXT")