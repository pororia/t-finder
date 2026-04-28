from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.toilet_service import ToiletService
from app.schemas.common import APIResponse
from app.repositories.toilet_repository import ToiletRepository
from app.utils.geo import location_to_dict

router = APIRouter()


@router.get("/nearby", response_model=APIResponse)
async def nearby_toilets(
    lat: float,
    lng: float,
    radius: int = 1000,
    db: AsyncSession = Depends(get_db),
):
    service = ToiletService(db)
    result = await service.get_nearby(lat, lng, radius)
    return APIResponse.ok({"results": result})


@router.get("/search", response_model=APIResponse)
async def search_toilets(
    q: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ToiletRepository(db)
    toilets = await repo.search_keyword(q)
    result = [
        {
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
            "photos": [{"id": str(p.id), "image_url": p.image_url, "display_order": p.display_order} for p in t.photos],
        }
        for t in toilets
    ]
    return APIResponse.ok({"results": result})


@router.get("/in-bounds", response_model=APIResponse)
async def in_bounds_toilets(
    min_lat: float,
    min_lng: float,
    max_lat: float,
    max_lng: float,
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import text
    # ST_X/ST_Y로 geography를 float 으로 직접 추출 → asyncpg geography 디코딩 우회
    rows = (
        await db.execute(
            text("""
                SELECT
                    id::text,
                    name,
                    address,
                    cleanliness,
                    ST_Y(location::geometry) AS lat,
                    ST_X(location::geometry) AS lng,
                    is_unisex,
                    is_accessible,
                    payment_type::text AS payment_type,
                    cost,
                    has_password,
                    male_seat_count,
                    male_urinal_count,
                    female_seat_count
                FROM toilets
                WHERE is_deleted = FALSE
                  AND ST_Intersects(
                        location,
                        ST_MakeEnvelope(:min_lng, :min_lat, :max_lng, :max_lat, 4326)::geography
                      )
                LIMIT 200
            """),
            {
                "min_lng": min_lng, "min_lat": min_lat,
                "max_lng": max_lng, "max_lat": max_lat,
            },
        )
    ).mappings().all()

    result = [
        {
            "id": row["id"],
            "name": row["name"],
            "address": row["address"],
            "cleanliness": row["cleanliness"],
            "location": {"lat": float(row["lat"]), "lng": float(row["lng"])},
            "is_unisex": row["is_unisex"],
            "is_accessible": row["is_accessible"],
            "payment_type": row["payment_type"],
            "cost": row["cost"],
            "has_password": row["has_password"],
            "male_seat_count": row["male_seat_count"],
            "male_urinal_count": row["male_urinal_count"],
            "female_seat_count": row["female_seat_count"],
        }
        for row in rows
    ]
    return APIResponse.ok({"results": result})
