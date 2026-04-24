from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.session import get_db
from app.services.toilet_service import ToiletService
from app.schemas.toilet import ToiletCreate, ToiletUpdate, ToiletResponse, ToiletHistoryResponse
from app.schemas.common import APIResponse
from app.core.dependencies import get_current_user, get_current_user_optional
from app.utils.geo import location_to_dict

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("", response_model=APIResponse)
async def list_toilets(
    offset: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.toilet_repository import ToiletRepository
    repo = ToiletRepository(db)
    toilets = await repo.get_list(offset=offset, limit=min(limit, 100))
    result = []
    for t in toilets:
        avg, cnt = await repo.get_avg_rating(str(t.id))
        d = {
            "id": str(t.id),
            "address": t.address,
            "name": t.name,
            "cleanliness": t.cleanliness,
            "location": location_to_dict(t.location),
            "is_unisex": t.is_unisex,
            "is_accessible": t.is_accessible,
            "payment_type": str(t.payment_type),
            "cost": t.cost,
            "has_password": t.has_password,
            "avg_rating": avg,
            "review_count": cnt,
            "photos": [{"id": str(p.id), "image_url": p.image_url, "display_order": p.display_order} for p in t.photos],
            "created_at": t.created_at.isoformat(),
            "updated_at": t.updated_at.isoformat(),
        }
        result.append(d)
    return APIResponse.ok({"results": result, "total": len(result)})


@router.post("", response_model=APIResponse)
@limiter.limit("5/minute")
async def create_toilet(
    request: Request,
    body: ToiletCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ToiletService(db)
    data = body.model_dump()
    toilet = await service.create_toilet(data, str(current_user.id))
    return APIResponse.ok({"id": str(toilet.id), "message": "화장실이 등록되었습니다."})


@router.get("/{toilet_id}", response_model=APIResponse)
async def get_toilet(
    toilet_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    service = ToiletService(db)
    toilet = await service.get_toilet(str(toilet_id), current_user)
    avg_rating = getattr(toilet, "_avg_rating", None)
    review_count = getattr(toilet, "_review_count", 0)
    decrypted_pw = getattr(toilet, "_decrypted_password", None)
    result = {
        "id": str(toilet.id),
        "address": toilet.address,
        "address_detail": toilet.address_detail,
        "name": toilet.name,
        "cleanliness": toilet.cleanliness,
        "description": toilet.description,
        "location": location_to_dict(toilet.location),
        "has_password": toilet.has_password,
        "password_value": decrypted_pw,
        "is_unisex": toilet.is_unisex,
        "is_accessible": toilet.is_accessible,
        "seat_count": toilet.seat_count,
        "urinal_count": toilet.urinal_count,
        "payment_type": str(toilet.payment_type),
        "cost": toilet.cost,
        "avg_rating": avg_rating,
        "review_count": review_count,
        "photos": [{"id": str(p.id), "image_url": p.image_url, "display_order": p.display_order} for p in toilet.photos],
        "created_by": str(toilet.created_by),
        "created_at": toilet.created_at.isoformat(),
        "updated_at": toilet.updated_at.isoformat(),
    }
    return APIResponse.ok(result)


@router.put("/{toilet_id}", response_model=APIResponse)
async def update_toilet(
    toilet_id: UUID,
    body: ToiletUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ToiletService(db)
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    toilet = await service.update_toilet(str(toilet_id), data, str(current_user.id))
    return APIResponse.ok({"id": str(toilet.id), "message": "수정되었습니다."})


@router.delete("/{toilet_id}", response_model=APIResponse)
async def delete_toilet(
    toilet_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ToiletService(db)
    is_admin = str(current_user.role) in ("ADMIN", "UserRole.ADMIN")
    await service.delete_toilet(str(toilet_id), str(current_user.id), is_admin=is_admin)
    return APIResponse.ok({"message": "삭제되었습니다."})


@router.get("/{toilet_id}/history", response_model=APIResponse)
async def get_toilet_history(
    toilet_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.toilet_repository import ToiletRepository
    repo = ToiletRepository(db)
    history_list = await repo.get_history(str(toilet_id))
    result = [
        {
            "id": str(h.id),
            "toilet_id": str(h.toilet_id),
            "snapshot": h.snapshot,
            "changed_fields": h.changed_fields,
            "change_type": h.change_type,
            "changed_by": str(h.changed_by),
            "changed_at": h.changed_at.isoformat(),
        }
        for h in history_list
    ]
    return APIResponse.ok({"results": result})
