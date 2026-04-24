from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from app.repositories.toilet_repository import ToiletRepository
from app.repositories.user_repository import UserRepository
from app.services.history_service import HistoryService
from app.core.exceptions import ToiletNotFoundException, ForbiddenException
from app.utils.encryption import encrypt_password, decrypt_password
from typing import Optional
import json


class ToiletService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.toilet_repo = ToiletRepository(db)
        self.history_service = HistoryService(db)

    def _toilet_to_dict(self, toilet) -> dict:
        return {
            "address": toilet.address,
            "address_detail": toilet.address_detail,
            "name": toilet.name,
            "cleanliness": toilet.cleanliness,
            "description": toilet.description,
            "has_password": toilet.has_password,
            "is_unisex": toilet.is_unisex,
            "is_accessible": toilet.is_accessible,
            "seat_count": toilet.seat_count,
            "urinal_count": toilet.urinal_count,
            "payment_type": str(toilet.payment_type),
            "cost": toilet.cost,
        }

    async def create_toilet(self, data: dict, user_id: str):
        location_data = data.pop("location")
        point = from_shape(Point(location_data["lng"], location_data["lat"]), srid=4326)
        data["location"] = point
        data["created_by"] = user_id

        if data.get("has_password") and data.get("password_value"):
            data["password_value"] = encrypt_password(data["password_value"])

        toilet = await self.toilet_repo.create(data)

        await self.history_service.record_change(
            toilet_id=str(toilet.id),
            old_data={},
            new_data=self._toilet_to_dict(toilet),
            change_type="CREATE",
            changed_by=user_id,
        )
        await self.db.commit()
        await self.db.refresh(toilet)
        return toilet

    async def get_toilet(self, toilet_id: str, current_user=None):
        toilet = await self.toilet_repo.get_by_id(toilet_id)
        if not toilet:
            raise ToiletNotFoundException()
        avg_rating, review_count = await self.toilet_repo.get_avg_rating(toilet_id)
        toilet._avg_rating = avg_rating
        toilet._review_count = review_count
        # 비밀번호는 로그인 사용자에게만 복호화 후 노출
        if toilet.has_password and toilet.password_value:
            if current_user:
                toilet._decrypted_password = decrypt_password(toilet.password_value)
            else:
                toilet._decrypted_password = None
        else:
            toilet._decrypted_password = None
        return toilet

    async def update_toilet(self, toilet_id: str, data: dict, user_id: str):
        toilet = await self.toilet_repo.get_by_id(toilet_id)
        if not toilet:
            raise ToiletNotFoundException()
        if str(toilet.created_by) != str(user_id):
            raise ForbiddenException("본인이 등록한 화장실만 수정할 수 있습니다.")

        old_data = self._toilet_to_dict(toilet)

        if "password_value" in data and data["password_value"]:
            data["password_value"] = encrypt_password(data["password_value"])

        toilet = await self.toilet_repo.update(toilet, data)
        new_data = self._toilet_to_dict(toilet)

        await self.history_service.record_change(
            toilet_id=toilet_id,
            old_data=old_data,
            new_data=new_data,
            change_type="UPDATE",
            changed_by=user_id,
        )
        await self.db.commit()
        await self.db.refresh(toilet)
        return toilet

    async def delete_toilet(self, toilet_id: str, user_id: str, is_admin: bool = False):
        toilet = await self.toilet_repo.get_by_id(toilet_id)
        if not toilet:
            raise ToiletNotFoundException()
        if not is_admin and str(toilet.created_by) != str(user_id):
            raise ForbiddenException("본인이 등록한 화장실만 삭제할 수 있습니다.")

        old_data = self._toilet_to_dict(toilet)
        await self.toilet_repo.soft_delete(toilet)
        await self.history_service.record_change(
            toilet_id=toilet_id,
            old_data=old_data,
            new_data={},
            change_type="DELETE",
            changed_by=user_id,
        )
        await self.db.commit()

    async def get_nearby(self, lat: float, lng: float, radius_m: int = 1000):
        rows = await self.toilet_repo.find_nearby(lat, lng, radius_m)
        result = []
        for toilet, distance in rows:
            thumbnail_url = None
            if toilet.photos:
                thumbnail_url = toilet.photos[0].image_url
            result.append({
                "id": str(toilet.id),
                "address": toilet.address,
                "location": self._get_location(toilet),
                "cleanliness": toilet.cleanliness,
                "is_unisex": toilet.is_unisex,
                "is_accessible": toilet.is_accessible,
                "payment_type": str(toilet.payment_type),
                "cost": toilet.cost,
                "has_password": toilet.has_password,
                "thumbnail_url": thumbnail_url,
                "distance_m": float(distance),
            })
        return result

    def _get_location(self, toilet) -> dict:
        from geoalchemy2.shape import to_shape
        try:
            shape = to_shape(toilet.location)
            return {"lat": shape.y, "lng": shape.x}
        except Exception:
            return {"lat": 0, "lng": 0}
