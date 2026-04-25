from fastapi import APIRouter
from app.api.v1 import auth, users, toilets, search, photos, reviews

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["인증"])
api_router.include_router(users.router, prefix="/users", tags=["사용자"])
api_router.include_router(search.router, prefix="/toilets", tags=["검색"])
api_router.include_router(toilets.router, prefix="/toilets", tags=["화장실"])
api_router.include_router(photos.router, prefix="/toilets", tags=["사진"])
api_router.include_router(reviews.router, prefix="", tags=["리뷰"])
