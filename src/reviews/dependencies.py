from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.dependencies import get_current_user
from typing import Annotated
from src.db.models import User

# Session = Depends(get_session)
CurrentUser = Annotated[User, Depends(get_current_user)]


async def is_review_owner(
    review_id: str,
    user: CurrentUser,
    session: AsyncSession = Depends(get_session),
):
    from .service import ReviewService

    review_service = ReviewService()
    review = await review_service.get_review(id=review_id, session=session)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot perform this action",
        )
    return review
