from uuid import UUID, uuid4
from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship
from fastapi_filter.contrib.sqlalchemy import Filter


class PatientBase(SQLModel):
    code: str = Field(default=None, unique=True)
    diagnosis: str | None = None

    clinic: Optional["Clinic"] = Relationship(back_populates="patients")

    desync_datas: List["DesyncDatas"] | None = Relationship(sa_relationship_kwargs={"cascade": "all, delete"},
                                                            back_populates="patient")

    clinic_uuid: UUID | None = Field(default=None, foreign_key="clinic.uuid")


class Patient(PatientBase, table=True):
    uuid: UUID | None = Field(default_factory=uuid4, nullable=False, primary_key=True)


class PatientCreate(SQLModel):
    code: str = Field(default=None, unique=True)
    diagnosis: str | None = None


class PatientRead(PatientCreate):
    pass


class PatientFilter(Filter):
    code__ilike: Optional[str] = Field(alias="code")

    class Constants(Filter.Constants):
        model = Patient

    class Config:
        allow_population_by_field_name = True


class PatientFilter(Filter):
    code__ilike: Optional[str] = Field(alias="code")

    class Constants(Filter.Constants):
        model = Patient

    class Config:
        allow_population_by_field_name = True

