from uuid import UUID, uuid4
from typing import Optional
from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship


class ClinicAddressBase(SQLModel):
    region: str
    city: str
    street: str
    build: str | None
    phone: str | None = None
    email: EmailStr | None = None  # или  email_validator  ?

    clinic_uuid: UUID | None = Field(default=None, foreign_key="clinic.uuid")


class ClinicAddress(ClinicAddressBase, table=True):
    uuid: UUID | None = Field(default_factory=uuid4, nullable=False, primary_key=True)
    clinic: Optional["Clinic"] = Relationship(back_populates="clinic_address")


class ClinicAddressCreate(SQLModel):
    region: str
    city: str
    street: str
    build: str | None
    phone: str | None = None
    email: EmailStr | None = None


class ClinicAddressRead(ClinicAddressBase):
    pass


class ClinicAddressUpdate(ClinicAddressCreate):
    pass
