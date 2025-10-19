from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from datetime import date, datetime 
import uuid

class Book(SQLModel, table=True):
    __tablename__ : str = "books"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str
    rating: float
    created_at: datetime = Field(sa_column=
        Column(pg.TIMESTAMP, default=datetime.now)
    )
    updated_at: datetime = Field(sa_column=
        Column(pg.TIMESTAMP, default=datetime.now)
    )


    def __repr__(self) -> str:
        return f"<Book {self.title}>"