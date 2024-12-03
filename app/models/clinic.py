from typing import Optional, List
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship

from models.clinicaddress import ClinicAddress


class ClinicBase(SQLModel):
    name: str = Field(default=None, unique=True)
    description: str | None = None
    logo: str | None = None

    users: List["User"] | None = Relationship(sa_relationship_kwargs={"cascade": "all, delete"},
                                              back_populates="clinic")
    devices: List["Device"] | None = Relationship(sa_relationship_kwargs={"cascade": "all, delete"},
                                                  back_populates="clinic")
    patients: List["Patient"] | None = Relationship(sa_relationship_kwargs={"cascade": "all, delete"},
                                                    back_populates="clinic")


class Clinic(ClinicBase, table=True):
    uuid: UUID = Field(default_factory=uuid4, nullable=False, primary_key=True)
    clinic_address: Optional["ClinicAddress"] = Relationship(sa_relationship_kwargs={'lazy': 'selectin'},
                                                             back_populates="clinic")


class ClinicCreate(ClinicBase):
    clinic_address: Optional["ClinicAddress"] = Relationship(sa_relationship_kwargs={'lazy': 'selectin'},
                                                             back_populates="clinic")


class ClinicRead(ClinicBase):
    uuid: UUID
    clinic_address: List["ClinicAddress"] | None = []


ClinicRead.update_forward_refs()
