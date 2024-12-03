from typing import List

from sqlmodel import SQLModel
from models import device, device_type, user, type_research


class AdminPanel(SQLModel):
    clinic_name: str | None = None
    clinic_logo: bytes | None = None
    user: List["user.UserRead"] | None = []
    # devices: List["device.Device"] | None = []
    devices: list | None = []
    device_types: List["device_type.DeviceType"] | None = []
    type_research: List["type_research.TypeResearch"] | None = []
