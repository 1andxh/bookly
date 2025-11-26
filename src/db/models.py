from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from datetime import date, datetime
import uuid
from typing import Optional

# from src.auth import models
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import String, Enum as SAEnum
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime
from sqlalchemy.ext import declarative
from enum import Enum
from typing import Optional, List

# from src.books import models


class Book(SQLModel, table=True):
    __tablename__: str = "books"

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str
    rating: float
    user: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    added_by: Optional["User"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(SQLModel, table=True):
    __tablename__: str = "users"

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    username: str
    password_hash: str = Field(
        sa_column=Column(String(255), nullable=False), exclude=True
    )
    email: str = Field(sa_column=Column(String(50), nullable=False))
    firstname: str = Field(sa_column=Column(String(50), nullable=False))
    lastname: str = Field(sa_column=Column(String(50), nullable=False))
    role: Role = Field(
        sa_column=Column(
            SAEnum(Role, name="role_enum", native_enum=False),
            nullable=False,
            server_default=Role.USER.value,
        ),
        # default=Role.USER.value
    )
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List["Book"] = Relationship(
        back_populates="added_by", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: List["Review"] = Relationship(
        back_populates="added_by", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Review(SQLModel, table=True):
    __tablename__: str = "reviews"

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    review_text: str
    rating: float = Field(le=5)
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    book_id: Optional[uuid.UUID] = Field(default=None, foreign_key="books.id")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    added_by: Optional[User] = Relationship(back_populates="reviews")
    book: Optional[Book] = Relationship(back_populates="reviews")
