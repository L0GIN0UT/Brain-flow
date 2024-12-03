from uuid import UUID, uuid4
from typing import Optional, List

from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship
from fastapi_filter.contrib.sqlalchemy import Filter


class UserBase(SQLModel):
    password: str
    last_name: str | None
    first_name: str | None
    patronymic: str | None
    phone: str | None = None
    email: EmailStr = Field(default='test@desync.com', unique=True)
    avatar: str | None = None
    profession: str | None = None

    clinic: Optional["Clinic"] = Relationship(back_populates="users")
    clinic_uuid: UUID = Field(default=None, foreign_key="clinic.uuid")

    desync_datas: List["DesyncDatas"] | None = Relationship(sa_relationship_kwargs={"cascade": "all, delete"},
                                                            back_populates="user")


class User(UserBase, table=True):
    uuid: UUID = Field(default_factory=uuid4, nullable=False, primary_key=True)


class UserCreate(SQLModel):
    password: str
    last_name: str | None
    first_name: str | None
    patronymic: str | None
    phone: str | None = None
    email: EmailStr = Field(default='test@desync.com', unique=True)
    avatar: str | None = None
    profession: str | None = None


class UserRead(SQLModel):
    uuid: UUID | None
    last_name: str | None
    first_name: str | None
    patronymic: str | None
    phone: str | None = None
    email: EmailStr | None
    avatar: str | None = None
    profession: str | None = None


class UserUpdate(SQLModel):
    password: str | None
    last_name: str | None
    first_name: str | None
    patronymic: str | None
    phone: str | None = None
    email: EmailStr | None
    avatar: str | None = None
    profession: str | None = None


class UserAuthorization(SQLModel):
    email: EmailStr = Field(default='test@desync.com')
    password: str


class UserRecoveryPassword(SQLModel):
    email: EmailStr = Field(default='test@desync.com')


class UserFilter(Filter):
    last_name__ilike: Optional[str] = Field(alias="last_name")
    first_name__ilike: Optional[str] = Field(alias="first_name")

    class Constants(Filter.Constants):
        model = User

    class Config:
        allow_population_by_field_name = True

