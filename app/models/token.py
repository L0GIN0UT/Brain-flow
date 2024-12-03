from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class Token(SQLModel):
    # uuid: UUID = Field(default_factory=uuid4, nullable=False, primary_key=True)
    access_token: str
    token_type: str
