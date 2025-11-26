from src.db.models import Review
from src.auth.service import UserAuthService
from src.books.service import BookService
from pydantic import EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import ReviewCreateModel, ReviewModel
from fastapi.exceptions import HTTPException
from fastapi import status, Depends
import logging
from sqlmodel import select, desc
from .dependencies import is_review_owner
from typing import Annotated

book_service = BookService()
user_service = UserAuthService()


class ReviewService:
    async def add_review(
        self,
        email: EmailStr,
        book_id: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ):

        try:
            book = await book_service.get_book(id=book_id, session=session)
            user = await user_service.get_user_by_email(email=email, session=session)

            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="book does not exist"
                )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
                )
            review_dict = review_data.model_dump()
            review = Review(**review_dict)

            review.added_by = user
            review.book = book

            session.add(review)
            await session.commit()
            return review

        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong!",
            )

    async def get_all_reviews(self, session: AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_review(self, id: str, session: AsyncSession):
        statement = select(Review).where(Review.id == id)
        result = await session.exec(statement)
        return result.first()

    # async def delete_review(self, id: str, email: str, session: AsyncSession):
    #     user = await user_service.get_user_by_email(email=email, session=session)

    #     review = await self.get_review(id=id, session=session)

    #     if not review or not user:
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail="Cannot delete this review"
    #         )

    #     await session.delete(review)
    #     await session.commit()

    async def delete_review(
        self,
        instance: Annotated[Review, Depends(is_review_owner)],
        session: AsyncSession,
    ):

        await session.delete(instance)
        await session.commit()
        return {"detail": "resource deleted"}
