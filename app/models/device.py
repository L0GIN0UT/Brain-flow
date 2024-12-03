from uuid import UUID, uuid4
from typing import List, Optional

from fastapi_filter import FilterDepends, with_prefix
from sqlmodel import Field, SQLModel, Relationship
from fastapi_filter.contrib.sqlalchemy import Filter

from models.device_type_link import DeviceDeviceTypeLink
from models.device_type import DeviceType, DeviceTypeFilter


class DeviceBase(SQLModel):
    name: str = Field(default=None, unique=True)
    description: str | None = None

    clinic: Optional["Clinic"] = Relationship(back_populates="devices")

    desync_datas: List["DesyncDatas"] | None = Relationship(sa_relationship_kwargs={"cascade": "all, delete"},
                                                            back_populates="device")

    clinic_uuid: UUID | None = Field(default=None, foreign_key="clinic.uuid")


class Device(DeviceBase, table=True):
    uuid: UUID | None = Field(default_factory=uuid4, nullable=False, primary_key=True)
    device_types: List["DeviceType"] | None = Relationship(sa_relationship_kwargs={'lazy': 'selectin'},
                                                           back_populates="device", link_model=DeviceDeviceTypeLink)
    status: bool | None = None


class DeviceCreate(SQLModel):
    name: str = Field(default=None, unique=True)
    description: str | None = None
    device_types: list | None = []


class DeviceRead(DeviceBase):
    uuid: UUID | None = None
    device_types: List["DeviceType"] | None = []
    status: bool | None = None


class DeviceUpdate(DeviceCreate):
    pass


class DeviceFilter(Filter):
    name__ilike: Optional[str] = Field(alias="name")
    # device_types__in: Optional[list[DeviceType]] = Field(alias="type")
    device_type: Optional[DeviceTypeFilter] = FilterDepends(with_prefix('device_type', DeviceTypeFilter))

    class Constants(Filter.Constants):
        model = Device

    class Config:
        allow_population_by_field_name = True

class DeviceFilterNoType(Filter):
    name__ilike: Optional[str] = Field(alias="name")
    # Убираем поле device_type

    class Constants(Filter.Constants):
        model = Device

    class Config:
        allow_population_by_field_name = True


DeviceRead.update_forward_refs()
