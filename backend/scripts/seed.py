"""시드 데이터 스크립트 - 서울 주요 지역 화장실 10개"""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://tfinder:tfinder_dev_password@localhost:5432/tfinder")

SEED_TOILETS = [
    {"name": "강남역 2번 출구 화장실", "address": "서울특별시 강남구 강남대로 396", "lat": 37.4979, "lng": 127.0276, "cleanliness": 4, "is_unisex": False, "is_accessible": True, "seat_count": 3, "urinal_count": 2, "payment_type": "FREE"},
    {"name": "홍대입구역 화장실", "address": "서울특별시 마포구 양화로 160", "lat": 37.5573, "lng": 126.9254, "cleanliness": 3, "is_unisex": False, "is_accessible": True, "seat_count": 4, "urinal_count": 3, "payment_type": "FREE"},
    {"name": "명동 관광안내소 화장실", "address": "서울특별시 중구 명동길 74", "lat": 37.5636, "lng": 126.9822, "cleanliness": 5, "is_unisex": False, "is_accessible": True, "seat_count": 5, "urinal_count": 4, "payment_type": "FREE"},
    {"name": "이태원역 화장실", "address": "서울특별시 용산구 이태원로 180", "lat": 37.5345, "lng": 126.9940, "cleanliness": 3, "is_unisex": False, "is_accessible": True, "seat_count": 2, "urinal_count": 2, "payment_type": "FREE"},
    {"name": "종로3가 화장실", "address": "서울특별시 종로구 종로 198", "lat": 37.5713, "lng": 126.9915, "cleanliness": 2, "is_unisex": False, "is_accessible": False, "seat_count": 3, "urinal_count": 3, "payment_type": "FREE"},
    {"name": "신촌역 화장실", "address": "서울특별시 서대문구 신촌로 83", "lat": 37.5551, "lng": 126.9368, "cleanliness": 4, "is_unisex": False, "is_accessible": True, "seat_count": 3, "urinal_count": 2, "payment_type": "FREE"},
    {"name": "동대문역사문화공원역 화장실", "address": "서울특별시 중구 을지로7가 2-1", "lat": 37.5644, "lng": 127.0092, "cleanliness": 3, "is_unisex": False, "is_accessible": True, "seat_count": 4, "urinal_count": 3, "payment_type": "FREE"},
    {"name": "압구정 공공 화장실", "address": "서울특별시 강남구 압구정로 167", "lat": 37.5271, "lng": 127.0330, "cleanliness": 4, "is_unisex": True, "is_accessible": True, "seat_count": 2, "urinal_count": 0, "payment_type": "FREE"},
    {"name": "여의도 한강공원 화장실", "address": "서울특별시 영등포구 여의동로 330", "lat": 37.5285, "lng": 126.9340, "cleanliness": 3, "is_unisex": False, "is_accessible": True, "seat_count": 4, "urinal_count": 4, "payment_type": "FREE"},
    {"name": "광화문광장 화장실", "address": "서울특별시 종로구 세종대로 172", "lat": 37.5759, "lng": 126.9768, "cleanliness": 5, "is_unisex": False, "is_accessible": True, "seat_count": 5, "urinal_count": 5, "payment_type": "FREE"},
]


async def run_seed():
    engine = create_async_engine(DATABASE_URL, echo=True)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        # 관리자 사용자 생성
        from app.db.models.user import User
        from app.db.models.toilet import Toilet, PaymentType
        from sqlalchemy import select

        admin_result = await session.execute(
            select(User).where(User.google_uid == "seed_admin_uid")
        )
        admin = admin_result.scalar_one_or_none()
        if not admin:
            admin = User(
                google_uid="seed_admin_uid",
                email="admin@t-finder.dev",
                nickname="관리자",
            )
            session.add(admin)
            await session.flush()

        for t_data in SEED_TOILETS:
            point = from_shape(Point(t_data["lng"], t_data["lat"]), srid=4326)
            toilet = Toilet(
                location=point,
                address=t_data["address"],
                name=t_data["name"],
                cleanliness=t_data["cleanliness"],
                is_unisex=t_data["is_unisex"],
                is_accessible=t_data["is_accessible"],
                seat_count=t_data["seat_count"],
                urinal_count=t_data.get("urinal_count", 0),
                payment_type=PaymentType(t_data["payment_type"]),
                created_by=admin.id,
            )
            session.add(toilet)

        await session.commit()
        print(f"시드 데이터 {len(SEED_TOILETS)}개 삽입 완료!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_seed())
