from fastapi import Request, status
from fastapi.security.http import HTTPAuthorizationCredentials
from typing_extensions import Annotated, Doc
from fastapi.security import HTTPBearer
from .utils import decode_token
from fastapi.exceptions import HTTPException
from typing import Any

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict[str, Any]:
        """get credentials from auth header"""
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(request)
        assert credentials is not None

        """extract token"""
        token = credentials.credentials

        """decode token"""
        token_data = decode_token(token)

        """check token validity"""    
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token or expired token!"
            )
           
        """check token type"""
        if token_data.get('refresh', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Provide access token"
            )

        return token_data
    
    def is_valid_token(self, token: str) -> bool:
        token_data = decode_token(token)

        if token_data is not None:
            return True
        
        return False
    

class AccessTokenBearer(TokenBearer):
    pass

class RefreshTokenBearer(TokenBearer):
    pass