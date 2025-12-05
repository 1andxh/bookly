from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from .schemas import (
    UserCreateModel,
    UserResponse,
    UserLoginModel,
    UserBookModel,
    EmailValidator,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from .service import UserAuthService
from src.db.models import User
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .utils import (
    create_access_token,
    hash_password,
    decode_token,
    verify_password,
    create_url_safe_token,
    decode_url_safe_token,
)
from datetime import timedelta, datetime
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from src.db.redis import add_jti_to_blocklist
from typing import Any
from src.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    InvalidCredentialsException,
    InvalidTokenException,
)
from src.mail import create_message, mail
from src.config import Config


auth_router = APIRouter()
user_auth_service = UserAuthService()
refresh_token_bearer = RefreshTokenBearer()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])
# bg_tasks = BackgroundTasks()
REFRESH_TOKEN_EXPIRY = 2


@auth_router.post("/send-mail")
async def send_mail(emails: EmailValidator):
    recipients = emails.addresses

    html = "<h1>Welcome to Bookly</h1>"

    message = create_message(
        receipients=recipients,
        subject="The 'Write place' to get all your books",
        body=html,
    )
    await mail.send_message(message=message)
    return {"message": "Email sent successfully"}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserCreateModel,
    bg_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    email = user_data.email

    user_exists = await user_auth_service.check_user_exists(email, session)

    if user_exists:
        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN, detail="User already exists"
        # )
        raise UserAlreadyExistsException(email)
    new_user = await user_auth_service.create_user(user_data, session)

    # generate verification token
    token = create_url_safe_token(data={"email": email})

    # todo: protocol can be used to switch between local/production
    # protocol = "http" if "localhost" in Config.DOMAIN else "https" or just save in .env and read

    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
        <h1>Verify Your Email Address</h1>
        <p>Hi {new_user.firstname},</p>
        <p>Thank you for signing up! Please verify your email address by clicking the button below:</p>
        
        <a href="{link}" style="display: inline-block; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0;">
            Verify Email
        </a>
        
        
        <p style="color: #666; font-size: 12px; margin-top: 30px;">
            If you didn't create an account, please ignore this email.
        </p>
        <p style="color: #666; font-size: 12px;">
            This link will expire in an hour.
        </p>
    </body>
    </html>
    """

    message = create_message(
        receipients=[email],
        subject="Verify your email address",
        body=html_content,
    )
    bg_tasks.add_task(mail.send_message, message)
    return {
        "message": "A link to veirfy your account as been sent to your email",
        "user": new_user,
    }

    # return new_user


@auth_router.get("/verify/{token}")
async def verify_user(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_auth_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFoundException

        await user_auth_service.update_user(user, {"is_verified": True}, session)
        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "An error occured"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


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
    # raise HTTPException(
    #     status_code=status.HTTP_403_FORBIDDEN,
    #     detail="Invalid login. Wrong Email or Password",
    # )
    raise InvalidCredentialsException()


@auth_router.post("/refresh")
async def refresh_token(token_data: dict = Depends(refresh_token_bearer)):
    expiry = token_data["exp"]
    if datetime.fromtimestamp(expiry) > datetime.now():
        new_access_token = create_access_token(user_data=token_data["user"])
        return JSONResponse(content={"access_token": new_access_token})
    raise InvalidTokenException()
    # raise HTTPException(
    #     status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
    # )


@auth_router.get("/me", response_model=UserBookModel)
async def get_my_user(user=Depends(get_current_user), _: bool = Depends(role_checker)):
    if not user:
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Invalid Authentication credentials",
        #     # headers=
        # )
        raise InvalidCredentialsException()
    return user


@auth_router.get("/logout")
async def revoke_token(token_data: dict = Depends(access_token_bearer)):
    jti = token_data["jti"]
    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={"message": "Logged Out"}, status_code=status.HTTP_200_OK
    )


@auth_router.post("/reset-password")
async def password_reset(data: PasswordResetRequest, bg_task: BackgroundTasks):
    email = data.email
    token = create_url_safe_token(data={"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/reset-password/{token}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1>Reset Your Password</h1>
        <p>We received a request to reset your password. Click the button below to create a new password:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{link}" 
            style="display: inline-block; 
                    padding: 12px 24px; 
                    background-color: #2196F3; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 4px;">
                Reset Password
            </a>
        </div>
        
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #0066cc; background: #f5f5f5; padding: 10px; border-radius: 4px;">
            {link}
        </p>
        
        <div style="color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
            <p><strong>If you didn't request a password reset, please ignore this email.</strong> Your password will remain unchanged.</p>
            <p>This link will expire in one hour for security reasons.</p>
        </div>
    </body>
    </html>
    """
    message = create_message(
        receipients=[email],
        subject="Reset Password",
        body=html_content,
    )
    bg_task.add_task(mail.send_message, message)

    return JSONResponse(
        content={"message": "A link to reset your password has been sent to your mail"},
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/reset-password-confirmation/{token}")
async def password_reset_confirmation(
    token: str,
    password: PasswordResetConfirm,
    session: AsyncSession = Depends(get_session),
):
    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if not user_email:
        raise InvalidTokenException()

    user = await user_auth_service.get_user_by_email(user_email, session)
    if not user:
        raise UserNotFoundException

    if password.new_password != password.confirm_new_password:
        raise HTTPException(
            detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
        )
    password_hash = hash_password(password.confirm_new_password)

    await user_auth_service.update_user(user, {"password_hash": password_hash}, session)
    return JSONResponse(
        content={"message": "Password reset successful"},
        status_code=status.HTTP_200_OK,
    )


# redundant --i wrote an exception for general exceptions
# return JSONResponse(
#     content={"message": "An error occured."},
#     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
# )
