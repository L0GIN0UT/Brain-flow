from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship
from fastapi_filter.contrib.sqlalchemy import Filter


class TypeResearchBase(SQLModel):
    name: str = Field(default=None, unique=True)
    description: str | None = None

    desync_datas: List["DesyncDatas"] | None = Relationship(sa_relationship_kwargs={"cascade": "all, delete"},
                                                            back_populates="type_research")


class TypeResearch(TypeResearchBase, table=True):
    uuid: UUID | None = Field(default_factory=uuid4, nullable=False, primary_key=True)


class TypeResearchCreate(TypeResearchBase):
    pass


class TypeResearchRead(TypeResearchBase):
    pass


class TypeResearchFilter(Filter):
    name__ilike: Optional[str] = Field(alias="name")

    class Constants(Filter.Constants):
        model = TypeResearch

    class Config:
        allow_population_by_field_name = True