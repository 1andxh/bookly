from fastapi import Request, status, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from typing import Annotated
from fastapi.security import HTTPBearer
from .utils import decode_token
from fastapi.exceptions import HTTPException
from typing import Any, override, List
from src.db.redis import token_in_blocklist
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .service import UserAuthService
from .models import User

user_auth_service = UserAuthService()

# reusable dependencies
# CurrentUser = Annotated[User, Depends(get_current_user)]
# TokenData = Annotated[dict[str, Any], Depends(AccessTokenBearer())]
# Session = Annotated[AsyncSession, Depends(get_session)]


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict[str, Any]:
        """get credentials from auth header"""
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(
            request
        )
        assert credentials is not None

        """extract token"""
        token = credentials.credentials

        """decode token"""
        token_data = decode_token(token)

        """check token validity"""
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or expired token!",
            )

        if await token_in_blocklist(token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or revoked token! Renew token",
            )

        self.verify_token_data(token_data)

        return token_data

    # def is_valid_token(self, token: str) -> bool:
    #     token_data = decode_token(token)
    #     if token_data is not None:
    #         return True
    #     return False

    def verify_token_data(self, token_data: dict[str, Any]):
        raise NotImplementedError("Please override this method in child classes")


class AccessTokenBearer(TokenBearer):
    @override
    def verify_token_data(self, token_data: dict[str, Any]) -> None:
        # check token type
        if token_data.get("refresh", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Provide access token"
            )


class RefreshTokenBearer(TokenBearer):
    @override
    def verify_token_data(self, token_data: dict[str, Any]) -> None:
        # check token type
        if not token_data.get("refresh", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Provide refresh token"
            )


async def get_current_user(
    token_data: dict[str, Any] = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user_email = token_data["user"]["email"]
    user = await user_auth_service.get_user_by_email(user_email, session)
    return user


# RBAC
CurrentUser = Annotated[User, Depends(get_current_user)]


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: CurrentUser) -> Any:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perfrom this action",
            )
        # return True
