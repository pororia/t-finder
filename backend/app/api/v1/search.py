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
    repo = ToiletRepository(db)
    toilets = await repo.find_in_bounds(min_lat, min_lng, max_lat, max_lng)
    result = [
        {
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
            "male_seat_count": t.male_seat_count,
            "male_urinal_count": t.male_urinal_count,
            "female_seat_count": t.female_seat_count,
        }
        for t in toilets
    ]
    return APIResponse.ok({"results": result})
