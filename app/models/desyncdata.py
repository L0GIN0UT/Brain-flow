from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship, Column, JSON, TIMESTAMP, text


class DesyncDatasBase(SQLModel):
    data: dict = Field(sa_column=Column(JSON), default={})
    date: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
    ))

    device: Optional["Device"] = Relationship(back_populates="desync_datas")
    patient: Optional["Patient"] = Relationship(back_populates="desync_datas")
    type_research: Optional["TypeResearch"] = Relationship(back_populates="desync_datas")
    user: Optional["User"] = Relationship(back_populates="desync_datas")

    device_uuid: UUID | None = Field(default=None, foreign_key="device.uuid")
    patient_uuid: UUID | None = Field(default=None, foreign_key="patient.uuid")
    type_research_uuid: UUID | None = Field(default=None, foreign_key="typeresearch.uuid")
    user_uuid: UUID | None = Field(default=None, foreign_key="user.uuid")

    # user= Relationship(sa_relationship_kwargs={"cascade": "delete"},
    #                back_populates="clinic")


class DesyncDatasBaseWithoutData(SQLModel):
    date: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    device_uuid: UUID | None = Field(default=None)
    patient_uuid: UUID | None = Field(default=None)
    type_research_uuid: UUID | None = Field(default=None)
    user_uuid: UUID | None = Field(default=None)
    uuid: UUID | None = Field(default=None)


class DesyncDatas(DesyncDatasBase, table=True):
    uuid: UUID | None = Field(default_factory=uuid4, nullable=False, primary_key=True)


class DesyncDatasCreate(DesyncDatasBase):
    pass


class DesyncDatasRead(DesyncDatas):
    research_status: str|None = Field(nullable=True, default='open')
