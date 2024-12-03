from uuid import UUID
from pydantic import Field
from enum import Enum
from .config_models import BaseConfig


class ConnectStatus(int, Enum):
    connect = 1
    disconnect = 0


class DesyncLevel(BaseConfig):
    uuid: UUID = Field(alias='id')
    patient: dict  # {'uuid': str}
    status: ConnectStatus
    device: str
    chanel_desync: dict  # {'chanel_name': float}
