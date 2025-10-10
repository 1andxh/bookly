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

@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_book(book_data: BookCreateModel, session: AsyncSession = Depends(get_session)):
    new_book = await book_service.create_book(book_data, session)

    return new_book


@book_router.delete("/b{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    # for book in books:
    #     if book["id"] == book_id:
    #         books.remove(book)
    #         return 
    if book_id not in books:
        print(f"no book with Id: {book_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    del books[book_id]

@book_router.patch("/{book_id}")
async def update_book(book_id: int, update_model: BookUpdateModel) -> dict:
    for book in books:
        if book["id"] == book_id:
            book["title"] = update_model.title
            book["author"] = update_model.author
            book["pulished_date"] = update_model.published_date
            book["publish"] = update_model.publisher
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@book_router.get("/{book_id}")
async def get_book(book_id: int, session: AsyncSession = Depends(get_session)):
    book = await book_service.get_book(book_id, session)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@book_router.get("/", response_model=list[Book])
async def get_all_books(session: AsyncSession = Depends(get_session)) -> Sequence[Book]:
    books = await book_service.get_all_books(session)
    return books
