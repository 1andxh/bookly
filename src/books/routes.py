from fastapi import APIRouter
from fastapi import Header, status, Depends
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated, Sequence
from src.books.schemas import Book, BookUpdateModel, BookCreateModel, BookReviewModel
from src.db.models import Book
from src.db.main import get_session
from src.books.service import BookService
from src.auth.dependencies import TokenBearer, AccessTokenBearer, RoleChecker
from typing import Any

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])
# TokenDetails = Annotated[dict, Depends(AccessTokenBearer())]


@book_router.get(
    "/{book_id}", dependencies=[Depends(role_checker)], response_model=BookReviewModel
)
async def get_book(
    book_id: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict[str, Any] = Depends(access_token_bearer),
):
    book = await book_service.get_book(book_id, session)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return book


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
    dependencies=[Depends(role_checker)],
)
async def create_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    user_id = token_details["user"]["user_id"]
    new_book = await book_service.create_book(book_data, user_id, session)

    return new_book


@book_router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(role_checker)],
)
async def delete_book(
    book_id: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict[str, Any] = Depends(access_token_bearer),
):
    book_to_delete = await book_service.delete_book(book_id, session)
    if book_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return None


@book_router.patch("/{book_id}", dependencies=[Depends(role_checker)])
async def update_book(
    book_id: str,
    update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict[str, Any] = Depends(access_token_bearer),
) -> dict:
    book_to_update = await book_service.update_book(book_id, update_data, session)
    if book_to_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return {"Update": book_to_update}


@book_router.get("/", response_model=list[Book], dependencies=[Depends(role_checker)])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict[str, Any] = Depends(access_token_bearer),
) -> Sequence[Book]:
    # print(credentials)
    books = await book_service.get_all_books(session)
    return books


@book_router.get(
    "/user/{user_id}", response_model=list[Book], dependencies=[Depends(role_checker)]
)
async def get_books_by_user(
    user_id: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict[str, Any] = Depends(access_token_bearer),
) -> Sequence[Book]:
    # print(credentials)
    books = await book_service.get_books_by_user(user_id, session)
    return books
