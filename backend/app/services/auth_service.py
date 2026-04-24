from firebase_admin import auth as firebase_auth
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token, create_refresh_token
from app.core.exceptions import UnauthorizedException
from app.repositories.user_repository import UserRepository
from app.core.firebase import get_firebase_app
from datetime import datetime, timezone


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def login_with_google(self, id_token: str) -> dict:
        get_firebase_app()
        try:
            decoded = firebase_auth.verify_id_token(id_token)
        except Exception as e:
            raise UnauthorizedException(f"유효하지 않은 ID 토큰입니다: {str(e)}")

        google_uid = decoded["uid"]
        email = decoded.get("email", "")
        name = decoded.get("name", email.split("@")[0] if email else "사용자")
        picture = decoded.get("picture")

        user = await self.user_repo.get_by_google_uid(google_uid)
        if not user:
            user = await self.user_repo.create({
                "google_uid": google_uid,
                "email": email,
                "nickname": name,
                "profile_image_url": picture,
            })
        else:
            await self.user_repo.update(user, {"last_login_at": datetime.now(timezone.utc)})

        await self.db.commit()

        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "nickname": user.nickname,
                "profile_image_url": user.profile_image_url,
            },
        }

    async def refresh_token(self, refresh_token: str) -> dict:
        from app.core.security import decode_token
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Refresh 토큰이 아닙니다.")
        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("유효하지 않은 사용자입니다.")
        new_access_token = create_access_token(subject=str(user.id))
        return {"access_token": new_access_token, "token_type": "bearer"}
