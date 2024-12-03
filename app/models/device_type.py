from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship
from fastapi_filter.contrib.sqlalchemy import Filter

from models.device_type_link import DeviceDeviceTypeLink


class DeviceTypeBase(SQLModel):
    name: str = Field(default=None, unique=True)
    description: str | None = None


class DeviceType(DeviceTypeBase, table=True):
    uuid: UUID | None = Field(default_factory=uuid4, nullable=False, primary_key=True)
    device: List["Device"] | None = Relationship(sa_relationship_kwargs={"cascade": "all, delete"},
                                                 back_populates="device_types", link_model=DeviceDeviceTypeLink)


class DeviceTypeCreate(DeviceTypeBase):
    pass


class DeviceTypeRead(DeviceTypeBase):
    uuid: UUID


class DeviceTypeFilter(Filter):
    name: Optional[str] = None
    name__like: Optional[str] = None

    class Constants(Filter.Constants):
        model = DeviceType

    class Config:
        allow_population_by_field_name = True