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
            "payment_type": t.payment_type.value if hasattr(t.payment_type, 'value') else str(t.payment_type),
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
    from sqlalchemy import text
    from app.core.exceptions import ToiletNotFoundException
    from app.utils.encryption import decrypt_password

    row = (await db.execute(
        text("""
            SELECT
                id::text,
                toilet_type::text AS toilet_type,
                address, address_jibun, address_detail, name,
                cleanliness, description,
                has_password, password_value,
                is_unisex, is_accessible,
                seat_count, urinal_count,
                male_seat_count, male_urinal_count,
                male_disabled_seat_count, male_disabled_urinal_count,
                male_children_seat_count, male_children_urinal_count,
                female_seat_count, female_disabled_seat_count, female_children_seat_count,
                open_hours,
                has_emergency_bell, emergency_bell_location,
                has_entrance_cctv, has_diaper_table, diaper_table_location,
                remodeling_date,
                payment_type::text AS payment_type,
                cost,
                created_by::text,
                created_at, updated_at,
                ST_Y(location::geometry) AS lat,
                ST_X(location::geometry) AS lng
            FROM toilets
            WHERE id = :id AND is_deleted = FALSE
        """),
        {"id": str(toilet_id)},
    )).mappings().one_or_none()

    if not row:
        raise ToiletNotFoundException()

    photos = (await db.execute(
        text("SELECT id::text, image_url, display_order FROM toilet_photos WHERE toilet_id = :id ORDER BY display_order"),
        {"id": str(toilet_id)},
    )).mappings().all()

    rating_row = (await db.execute(
        text("SELECT AVG(rating)::float AS avg_rating, COUNT(*)::int AS review_count FROM reviews WHERE toilet_id = :id"),
        {"id": str(toilet_id)},
    )).mappings().one()

    decrypted_pw = None
    if row["has_password"] and row["password_value"] and current_user:
        try:
            decrypted_pw = decrypt_password(row["password_value"])
        except Exception:
            pass

    result = {
        "id": row["id"],
        "address": row["address"],
        "address_jibun": row["address_jibun"],
        "address_detail": row["address_detail"],
        "name": row["name"],
        "cleanliness": row["cleanliness"],
        "description": row["description"],
        "location": {"lat": float(row["lat"]), "lng": float(row["lng"])},
        "has_password": row["has_password"],
        "password_value": decrypted_pw,
        "is_unisex": row["is_unisex"],
        "is_accessible": row["is_accessible"],
        "seat_count": row["seat_count"],
        "urinal_count": row["urinal_count"],
        "male_seat_count": row["male_seat_count"],
        "male_urinal_count": row["male_urinal_count"],
        "female_seat_count": row["female_seat_count"],
        "payment_type": row["payment_type"],
        "cost": row["cost"],
        "avg_rating": rating_row["avg_rating"],
        "review_count": rating_row["review_count"],
        "photos": [{"id": p["id"], "image_url": p["image_url"], "display_order": p["display_order"]} for p in photos],
        "created_by": row["created_by"],
        "created_at": row["created_at"].isoformat(),
        "updated_at": row["updated_at"].isoformat(),
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
