from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.db.session import get_db
from app.core.dependencies import get_current_user, get_current_user_optional
from app.schemas.toilet import ReviewCreate, ReviewUpdate
from app.schemas.common import APIResponse
from app.db.models.review import Review
from app.core.exceptions import ReviewNotFoundException, ForbiddenException, DuplicateReviewException, ToiletNotFoundException
from app.repositories.toilet_repository import ToiletRepository

router = APIRouter()


@router.get("/toilets/{toilet_id}/reviews", response_model=APIResponse)
async def list_reviews(
    toilet_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Review).where(Review.toilet_id == toilet_id).order_by(Review.created_at.desc())
    )
    reviews = result.scalars().all()
    data = [
        {
            "id": str(r.id),
            "toilet_id": str(r.toilet_id),
            "user_id": str(r.user_id),
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat(),
            "updated_at": r.updated_at.isoformat(),
        }
        for r in reviews
    ]
    return APIResponse.ok({"results": data})


@router.post("/toilets/{toilet_id}/reviews", response_model=APIResponse)
async def create_review(
    toilet_id: UUID,
    body: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    repo = ToiletRepository(db)
    toilet = await repo.get_by_id(str(toilet_id))
    if not toilet:
        raise ToiletNotFoundException()

    existing = await db.execute(
        select(Review).where(Review.toilet_id == toilet_id, Review.user_id == current_user.id)
    )
    if existing.scalar_one_or_none():
        raise DuplicateReviewException()

    review = Review(
        toilet_id=toilet_id,
        user_id=current_user.id,
        rating=body.rating,
        comment=body.comment,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return APIResponse.ok({"id": str(review.id), "message": "리뷰가 등록되었습니다."})


@router.put("/reviews/{review_id}", response_model=APIResponse)
async def update_review(
    review_id: UUID,
    body: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise ReviewNotFoundException()
    if str(review.user_id) != str(current_user.id):
        raise ForbiddenException("본인의 리뷰만 수정할 수 있습니다.")

    if body.rating is not None:
        review.rating = body.rating
    if body.comment is not None:
        review.comment = body.comment
    await db.commit()
    await db.refresh(review)
    return APIResponse.ok({"id": str(review.id), "message": "리뷰가 수정되었습니다."})


@router.delete("/reviews/{review_id}", response_model=APIResponse)
async def delete_review(
    review_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise ReviewNotFoundException()
    if str(review.user_id) != str(current_user.id):
        raise ForbiddenException("본인의 리뷰만 삭제할 수 있습니다.")

    await db.delete(review)
    await db.commit()
    return APIResponse.ok({"message": "리뷰가 삭제되었습니다."})
