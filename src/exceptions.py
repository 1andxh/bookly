from fastapi import status
from starlette.status import HTTP_401_UNAUTHORIZED

# class UnicornException(Exception):
#     def __init__(self, *args: object) -> None:
#         super().__init__(*args)
# class BaseExeption(BaseExecption)


class BooklyException(Exception):
    """
    Base class for all Exceptions
    """

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)


# auth related exceptions
class AuthenticationException(BooklyException):
    """Base class for all authentication/authorization exceptions"""

    def __init__(self, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(message, status_code)


class InvalidTokenException(AuthenticationException):
    """
    Invalid or expired token
    """

    def __init__(self):
        super().__init__(
            "invalid or expired token.", status_code=status.HTTP_401_UNAUTHORIZED
        )


class RevokedTokenException(AuthenticationException):
    """
    Raised when a revoked token has been provided
    """

    def __init__(self):
        super().__init__(
            "Token has been revoked, renew token.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AccessTokenRequiredException(AuthenticationException):
    """Raised when an access token is required but not provied"""

    def __init__(self):
        super().__init__(
            "Acess token required", status_code=status.HTTP_401_UNAUTHORIZED
        )


class RefreshTokenRequiredException(AuthenticationException):
    """Raised when an refresh token is required but not provied"""

    def __init__(self):
        super().__init__(
            "Provide refresh token", status_code=status.HTTP_401_UNAUTHORIZED
        )


class InvalidCredentialsException(AuthenticationException):
    """Raised when invalid credentials(email or password) is provided login"""

    def __init__(self):
        super().__init__(
            "Invalid email or password", status_code=status.HTTP_401_UNAUTHORIZED
        )


class UserAlreadyExistsException(AuthenticationException):
    """Raised when an attempt to sign up with an email that already exists is made"""

    def __init__(self, email: str):
        self.email = email
        super().__init__(
            f"User with email '{email}' already exists",
            status_code=status.HTTP_409_CONFLICT,
        )


class UserNotFoundException(AuthenticationException):
    """Raised when user not found"""

    def __init__(self):
        super().__init__("User not found", status_code=status.HTTP_404_NOT_FOUND)


class UserNotVerifiedException(AuthenticationException):
    """Raise when user isn't verified"""

    def __init__(self):
        super().__init__(
            "User account not verified. Check email to complete verification",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class InsufficientPermissionException(AuthenticationException):
    """Raised when user is not permitted to perform an action"""

    def __init__(self, action: str = "perform this action"):
        self.action = action
        super().__init__(
            f"You don't have permission to perfomr {action}",
            status_code=status.HTTP_403_FORBIDDEN,
        )


# class ResourceException(BooklyException):
#     """Base class for book-related errors"""


class BookNotFoundException(BooklyException):
    """Raised when book not found"""

    def __init__(self):

        super().__init__("Book not found", status_code=status.HTTP_404_NOT_FOUND)


# async def exception_handler():
#     pass


# exceptions_handlers = {}
