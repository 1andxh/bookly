from pydantic import BaseModel

class Book(BaseModel):
    id: int
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