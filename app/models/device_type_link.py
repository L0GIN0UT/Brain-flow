from uuid import UUID
from sqlmodel import Field, SQLModel


class DeviceDeviceTypeLink(SQLModel, table=True):
    __tablename__ = "device_device_type_link"
    device_uuid: UUID | None = Field(default=None, foreign_key="device.uuid", primary_key=True)
    device_types_uuid: UUID | None = Field(default=None, foreign_key="devicetype.uuid", primary_key=True)
