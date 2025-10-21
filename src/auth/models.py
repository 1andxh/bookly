from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime 

class User(SQLModel, table=True):
    __tablename__: str = "users"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4)
    )
    username: str
    password_hash: str = Field(
        sa_column=Column(String(255), nullable=False),
        exclude=True)
    email: str = Field(sa_column=Column(String(50), nullable=False))
    firstname: str = Field(sa_column=Column(String(50), nullable=False))
    lastname: str = Field(sa_column=Column(String(50), nullable=False))
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            default=datetime.now
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            default=datetime.now
        )
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"