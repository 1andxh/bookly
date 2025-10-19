from pydantic import BaseModel
import uuid
from datetime import datetime

class Book(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str
    rating: float
    created_at: datetime
    updated_at: datetime

class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str
    rating: float

class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str | None = None
    published_date: str
    page_count: int | None = None
    language: str | None = None
    rating: float | None = None
    