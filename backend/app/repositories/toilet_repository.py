from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_SetSRID, ST_MakePoint, ST_X, ST_Y, ST_AsGeoJSON
from app.db.models.toilet import Toilet
from app.db.models.review import Review
from typing import Optional, List
import json


class ToiletRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, toilet_id: str) -> Optional[Toilet]:
        result = await self.db.execute(
            select(Toilet)
            .options(selectinload(Toilet.photos), selectinload(Toilet.reviews))
            .where(Toilet.id == toilet_id, Toilet.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_list(self, offset: int = 0, limit: int = 20) -> List[Toilet]:
        result = await self.db.execute(
            select(Toilet)
            .options(selectinload(Toilet.photos))
            .where(Toilet.is_deleted == False)
            .offset(offset)
            .limit(limit)
            .order_by(Toilet.created_at.desc())
        )
        return list(result.scalars().all())

    async def find_nearby(self, lat: float, lng: float, radius_m: int = 1000, limit: int = 50):
        point = ST_SetSRID(ST_MakePoint(lng, lat), 4326)
        query = (
            select(
                Toilet,
                ST_Distance(Toilet.location, point.cast("geography")).label("distance_m"),
            )
            .where(
                Toilet.is_deleted == False,
                ST_DWithin(Toilet.location, point.cast("geography"), radius_m),
            )
            .order_by(text("distance_m"))
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.all()

    async def find_in_bounds(self, min_lat: float, min_lng: float, max_lat: float, max_lng: float) -> List[Toilet]:
        envelope = func.ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326).cast("geography")
        result = await self.db.execute(
            select(Toilet)
            .options(selectinload(Toilet.photos))
            .where(
                Toilet.is_deleted == False,
                func.ST_Intersects(Toilet.location, envelope),
            )
            .limit(200)
        )
        return list(result.scalars().all())

    async def search_keyword(self, keyword: str, limit: int = 20) -> List[Toilet]:
        result = await self.db.execute(
            select(Toilet)
            .options(selectinload(Toilet.photos))
            .where(
                Toilet.is_deleted == False,
                (
                    Toilet.address.ilike(f"%{keyword}%")
                    | Toilet.name.ilike(f"%{keyword}%")
                    | Toilet.description.ilike(f"%{keyword}%")
                ),
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, data: dict) -> Toilet:
        toilet = Toilet(**data)
        self.db.add(toilet)
        await self.db.flush()
        await self.db.refresh(toilet)
        return toilet

    async def update(self, toilet: Toilet, data: dict) -> Toilet:
        for key, value in data.items():
            setattr(toilet, key, value)
        await self.db.flush()
        await self.db.refresh(toilet)
        return toilet

    async def soft_delete(self, toilet: Toilet) -> Toilet:
        toilet.is_deleted = True
        await self.db.flush()
        return toilet

    async def get_history(self, toilet_id: str):
        from app.db.models.toilet_history import ToiletHistory
        result = await self.db.execute(
            select(ToiletHistory)
            .where(ToiletHistory.toilet_id == toilet_id)
            .order_by(ToiletHistory.changed_at.desc())
        )
        return list(result.scalars().all())

    async def get_avg_rating(self, toilet_id: str) -> tuple:
        result = await self.db.execute(
            select(func.avg(Review.rating), func.count(Review.id))
            .where(Review.toilet_id == toilet_id)
        )
        row = result.one()
        avg = float(row[0]) if row[0] else None
        count = row[1]
        return avg, count
