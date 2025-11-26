from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import List
from src.books.schemas import Book
from src.db.models import Role
from src.reviews.schemas import ReviewModel


class UserCreateModel(BaseModel):
    firstname: str = Field(max_length=24)
    lastname: str = Field(max_length=24)
    username: str = Field(max_length=24)
    email: str = Field(max_length=50)
    password: str = Field(min_length=8, max_length=255)


class UserResponse(BaseModel):
    id: uuid.UUID
    firstname: str
    lastname: str
    username: str
    email: str
    is_verified: bool
    role: Role
    created_at: datetime
    updated_at: datetime

    # class Config:
    #     user_enum_values = True


class UserBookModel(UserResponse):
    books: List[Book]
    reviews: List[ReviewModel]


class UserLoginModel(BaseModel):
    email: str = Field(max_length=50)
    password: str = Field(min_length=8, max_length=255)


class UserBase(BaseModel):
    email: str
    id: uuid.UUID
