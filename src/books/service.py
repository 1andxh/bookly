from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from src.db.models import Book
from datetime import datetime as dt
import uuid


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_book(self, id: str, session: AsyncSession):
        statement = select(Book).where(Book.id == id)
        result = await session.exec(statement)
        return result.first()

    async def get_books_by_user(self, user_id: str, session: AsyncSession):
        statement = (
            select(Book).where(Book.user == user_id).order_by(desc(Book.created_at))
        )
        result = await session.exec(statement)
        return result.all()

    async def create_book(
        self, book_data: BookCreateModel, user_id: uuid.UUID, session: AsyncSession
    ):
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.user = user_id

        #    new_book.published_date = dt.strptime(book_data_dict['published_date'], "%Y-%m-%d")
        session.add(new_book)
        await session.commit()
        return new_book

    async def update_book(
        self, id: str, update_data: BookUpdateModel, session: AsyncSession
    ):
        book_update = await self.get_book(id, session)
        if book_update is not None:
            update_data_dict = update_data.model_dump()

            for k, v in update_data_dict.items():
                setattr(book_update, k, v)

            await session.commit()
            return book_update
        return

    async def delete_book(self, id: str, session: AsyncSession):
        book_to_delete = await self.get_book(id, session)
        if book_to_delete is None:
            await session.delete(book_to_delete)
            await session.commit()
            return {"message": "book has been deleted"}
        return
