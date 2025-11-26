from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Optional


class ReviewModel(BaseModel):
    id: uuid.UUID
    rating: float = Field(le=5)
    review_text: str
    user_id: Optional[uuid.UUID]
    book_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime


class ReviewCreateModel(BaseModel):
    rating: float = Field(le=5)
    review_text: str
