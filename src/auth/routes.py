from fastapi import (
    APIRouter, 
    Depends, 
    status)
from fastapi.exceptions import HTTPException
from .schemas import UserCreateModel, UserResponse
from .service import UserAuthService
from .models import User
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession



auth_router = APIRouter()
user_auth_service = UserAuthService()

@auth_router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)) :
    email = user_data.email

    user_exists = await user_auth_service.check_user_exists(email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User already exists"
        )
    new_user = await user_auth_service.create_user(user_data, session)
    return new_user

