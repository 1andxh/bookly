from fastapi import APIRouter
from fastapi import FastAPI, Header, status
from fastapi.exceptions import HTTPException
from typing import Annotated
from src.books.schemas import Book, BookUpdateModel
from src.books.books import books

book_router = APIRouter()

@book_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(book: Book) -> dict:
    new_book = book.model_dump()
    books.append(new_book)
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
async def get_book(book_id: int) -> dict:
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not found"
        )

@book_router.get("/", response_model=list[Book])
async def get_all_books() -> list:
    return books
