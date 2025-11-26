from fastapi import APIRouter, Depends, status, HTTPException
from src.db.models import Review, User
from src.db.main import get_session
from src.auth.dependencies import get_current_user, RoleChecker
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import ReviewCreateModel
from .service import ReviewService
from typing import Annotated
from .dependencies import is_review_owner

review_router = APIRouter()
review_service = ReviewService()
CurrentUser = Annotated[User, Depends(get_current_user)]
admin_checker = Depends(RoleChecker(["admin"]))
user_checker = Depends(RoleChecker(["user", "admin"]))
Session = Annotated[AsyncSession, Depends(get_session)]


@review_router.get("/", dependencies=[admin_checker])
async def get_all_reviews(session: Session):
    reviews = await review_service.get_all_reviews(session=session)
    return reviews


@review_router.get("/{review_id}", dependencies=[user_checker])
async def get_review(review_id: str, session: Session):
    review = await review_service.get_review(id=review_id, session=session)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="review not found"
        )
    return review


@review_router.post("/book/{book_id}", dependencies=[user_checker])
async def add_review(
    book_id: str,
    user: CurrentUser,
    review: ReviewCreateModel,
    session: Session,
):
    new_review = await review_service.add_review(
        email=user.email, book_id=book_id, review_data=review, session=session
    )
    return new_review


@review_router.delete(
    "/reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[user_checker],
)
async def delete_review(session: Session, review=Depends(is_review_owner)):
    await review_service.delete_review(instance=review, session=session)
    return None
