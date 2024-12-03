from typing import Optional
from uuid import UUID, uuid4

from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy import ForeignKey, Column, String, Boolean, Table, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql

from sqlalchemy_utils import PhoneNumberType, EmailType
from pydantic import EmailStr

# Define the models
Base = declarative_base()


class Clinic(Base):
    __tablename__ = 'clinic'
    uuid: UUID = Column(postgresql.UUID(as_uuid=True), default=uuid4, nullable=False, primary_key=True)

    name: str = Column(String(100), nullable=False, unique=True)
    description: str | None = Column(String(100), nullable=True)
    logo: str | None = Column(String(150), nullable=True)

    clinic_address = relationship(
        argument="ClinicAddress",
        back_populates="clinic",
        cascade="all, delete",
        passive_deletes=True)

    device = relationship(
        argument="Device",
        back_populates="clinic",
        cascade="all, delete",
        passive_deletes=True)

    patient = relationship(
        argument="Patient",
        back_populates="clinic",
        cascade="all, delete",
        passive_deletes=True)

    user = relationship(
        argument="User",
        back_populates="clinic",
        cascade="all, delete",
        passive_deletes=True)


class ClinicAddress(Base):
    __tablename__ = 'clinicaddress'
    uuid: UUID = Column(postgresql.UUID(as_uuid=True), default=uuid4, nullable=False, primary_key=True)

    region: str = Column(String(100), nullable=False)
    city: str = Column(String(100), nullable=False)
    street: str = Column(String(100), nullable=False)
    build: str | None = Column(String(100), nullable=True)
    phone: PhoneNumber | None = Column(PhoneNumberType, nullable=True, unique=True)
    email: EmailStr | None = Column(EmailType, nullable=True)  # или  email_validator  ?

    clinic_uuid: UUID = Column(postgresql.UUID(as_uuid=True),
                               ForeignKey(column='clinic.uuid', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    clinic = relationship(argument="Clinic", back_populates="clinic_address")


device_device_type_link = Table(
    "device_device_type_link",
    Base.metadata,
    Column("device_uuid", ForeignKey("device.uuid", ondelete="CASCADE", onupdate="CASCADE"),
           primary_key=True),
    Column("device_types_uuid", ForeignKey("devicetype.uuid", ondelete="CASCADE", onupdate="CASCADE"),
           primary_key=True),
)


class Device(Base):
    __tablename__ = 'device'
    uuid: Optional[UUID] = Column(postgresql.UUID(as_uuid=True), default=uuid4, nullable=False, primary_key=True)

    name: str = Column(String(100), nullable=False, unique=True)
    description: str | None = Column(String(100), nullable=True)

    clinic_uuid: UUID = Column(postgresql.UUID(as_uuid=True),
                               ForeignKey(column='clinic.uuid', ondelete="CASCADE", onupdate="CASCADE"),
                               nullable=False
                               )

    clinic = relationship(argument="Clinic", back_populates="device")

    device_types_uuid = Column(postgresql.UUID(as_uuid=True),
                               ForeignKey(column='devicetype.uuid', ondelete="CASCADE", onupdate="CASCADE"),
                               nullable=True
                               )
    status: bool | None = Column(Boolean, nullable=True)
    device_types = relationship(
        argument="DeviceType",
        secondary=device_device_type_link,
        back_populates="device",
        cascade="all, delete",
        passive_deletes=True)

    desyncdatas = relationship(
        argument="DesyncDatas",
        back_populates="device",
        cascade="all, delete",
        passive_deletes=True)


class DeviceType(Base):
    __tablename__ = 'devicetype'
    uuid: Optional[UUID] = Column(postgresql.UUID(as_uuid=True), default=uuid4, nullable=False, primary_key=True)

    name: str = Column(String(100), nullable=False, unique=True)
    description: str | None = Column(String(100), nullable=True)

    device = relationship(
        argument="Device",
        secondary=device_device_type_link,
        back_populates="device_types",
        cascade="all, delete",
        passive_deletes=True)


class DesyncDatas(Base):
    __tablename__ = 'desyncdatas'
    uuid: Optional[UUID] = Column(postgresql.UUID(as_uuid=True), default=uuid4, nullable=False, primary_key=True)

    data: dict = Column(JSON, nullable=True)
    date: DateTime = Column(DateTime(timezone=True), nullable=True)

    device_uuid: UUID = Column(postgresql.UUID(as_uuid=True),
                               ForeignKey(column='device.uuid', ondelete="CASCADE", onupdate="CASCADE"),
                               nullable=False)
    user_uuid: UUID = Column(postgresql.UUID(as_uuid=True),
                             ForeignKey(column='user.uuid', ondelete="CASCADE", onupdate="CASCADE"),
                             nullable=False, index=True)
    patient_uuid: UUID = Column(postgresql.UUID(as_uuid=True),
                                ForeignKey(column='patient.uuid', ondelete="CASCADE", onupdate="CASCADE"),
                                nullable=False, index=True)
    type_research_uuid: UUID = Column(postgresql.UUID(as_uuid=True),
                                      ForeignKey(column='typeresearch.uuid', ondelete="CASCADE", onupdate="CASCADE"),
                                      nullable=False)

    device = relationship(argument="Device", back_populates="desyncdatas")
    user = relationship(argument="User", back_populates="desyncdatas")
    patient = relationship(argument="Patient", back_populates="desyncdatas")
    type_research = relationship(argument="TypeResearch", back_populates="desyncdatas")


class TypeResearch(Base):
    __tablename__ = 'typeresearch'
    uuid: Optional[UUID] = Column(postgresql.UUID(as_uuid=True), default=uuid4, nullable=False, primary_key=True)

    name: str = Column(String(100), nullable=False, unique=True)
    description: str | None = Column(String(100), nullable=True)

    desyncdatas = relationship(
        argument="DesyncDatas",
        back_populates="type_research",
        cascade="all, delete",
        passive_deletes=True)


class User(Base):
    __tablename__ = 'user'
    uuid: Optional[UUID] = Column(postgresql.UUID(as_uuid=True), default=uuid4, nullable=False, primary_key=True)

    password: str = Column(String, nullable=False)
    last_name: str | None = Column(String(100), nullable=True)
    first_name: str | None = Column(String(100), nullable=True)
    patronymic: str | None = Column(String(100), nullable=True)
    phone: PhoneNumber | None = Column(PhoneNumberType, nullable=True, unique=True)
    email: EmailStr = Column(EmailType, nullable=False, unique=True)
    avatar: str | None = Column(String(150), nullable=True, unique=True)
    profession: str | None = Column(String(100), nullable=True)

    clinic_uuid: UUID = Column(postgresql.UUID(as_uuid=True),
                               ForeignKey(column='clinic.uuid', ondelete="CASCADE", onupdate="CASCADE"),
                               nullable=False)

    clinic = relationship(argument="Clinic", back_populates="user")

    desyncdatas = relationship(
        argument="DesyncDatas",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True)


class Patient(Base):
    __tablename__ = 'patient'
    uuid: Optional[UUID] = Column(postgresql.UUID(as_uuid=True), default=uuid4, nullable=False, primary_key=True)

    code: str = Column(String(100), nullable=False, unique=True)
    diagnosis: str | None = Column(String(100), nullable=True)

    clinic_uuid: UUID = Column(postgresql.UUID(as_uuid=True),
                               ForeignKey(column='clinic.uuid', ondelete="CASCADE", onupdate="CASCADE"),
                               nullable=False)

    clinic = relationship(argument="Clinic", back_populates="patient")

    desyncdatas = relationship(
        argument="DesyncDatas",
        back_populates="patient",
        cascade="all, delete",
        passive_deletes=True)

