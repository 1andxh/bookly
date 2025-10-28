from pydantic import (
    BaseModel, 
    Field
)
import uuid
from datetime import datetime

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
    created_at: datetime
    updated_at: datetime 

class UserLoginModel(BaseModel):
    email: str = Field(max_length=50)
    password: str = Field(min_length=8, max_length=255)