from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from .schemas import UserCreateModel, UserResponse, UserLoginModel, UserBookModel
from .service import UserAuthService
from src.db.models import User
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .utils import create_access_token, decode_token, verify_password
from datetime import timedelta, datetime
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from src.db.redis import add_jti_to_blocklist
from typing import Any


auth_router = APIRouter()
user_auth_service = UserAuthService()
refresh_token_bearer = RefreshTokenBearer()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])
REFRESH_TOKEN_EXPIRY = 2


@auth_router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user_account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    email = user_data.email

    user_exists = await user_auth_service.check_user_exists(email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User already exists"
        )
    new_user = await user_auth_service.create_user(user_data, session)
    return new_user


@auth_router.post("/login")
async def login(login: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login.email
    password = login.password

    user = await user_auth_service.get_user_by_email(email, session)

    if user is not None:
        is_valid_password = verify_password(password, user.password_hash)

        if is_valid_password:
            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_id": str(user.id),
                    "role": user.role,
                }
            )
            refresh_token = create_access_token(
                user_data={"email": user.email, "user_id": str(user.id)},
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
                refresh=True,
            )
            return JSONResponse(
                content={
                    "message": "login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid login. Wrong Email or Password",
    )


@auth_router.post("/refresh")
async def refresh_token(token_data: dict = Depends(refresh_token_bearer)):
    expiry = token_data["exp"]
    if datetime.fromtimestamp(expiry) > datetime.now():
        new_access_token = create_access_token(user_data=token_data["user"])
        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
    )


@auth_router.get("/me", response_model=UserBookModel)
async def get_my_user(user=Depends(get_current_user), _: bool = Depends(role_checker)):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authentication credentials",
            # headers=
        )
    return user


@auth_router.get("/logout")
async def revoke_token(token_data: dict = Depends(access_token_bearer)):
    jti = token_data["jti"]
    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={"message": "Logged Out"}, status_code=status.HTTP_200_OK
    )
