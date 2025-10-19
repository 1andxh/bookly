from fastapi import APIRouter
from fastapi import Header, status, Depends
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated, Sequence
from src.books.schemas import Book, BookUpdateModel, BookCreateModel
from src.books.models import Book
from src.db.main import get_session
from src.books.service import BookService

book_router = APIRouter()
book_service =BookService()


@book_router.get("/{book_id}")
async def get_book(book_id: str, session: AsyncSession = Depends(get_session)):
    book = await book_service.get_book(book_id, session)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_book(book_data: BookCreateModel, session: AsyncSession = Depends(get_session)):
    new_book = await book_service.create_book(book_data, session)

    return new_book


@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: str, session: AsyncSession = Depends(get_session)):
    book_to_delete =  await book_service.delete_book(book_id, session)
    if book_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return None

@book_router.patch("/{book_id}")
async def update_book(book_id: str, update_data: BookUpdateModel, session: AsyncSession = Depends(get_session)) -> dict:
    book_to_update = await book_service.update_book(book_id, update_data, session)
    if book_to_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return {"Update": book_to_update}


@book_router.get("/", response_model=list[Book])
async def get_all_books(session: AsyncSession = Depends(get_session)) -> Sequence[Book]:
    books = await book_service.get_all_books(session)
    return books
