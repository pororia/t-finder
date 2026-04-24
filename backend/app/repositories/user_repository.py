from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from typing import Optional


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_google_uid(self, google_uid: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.google_uid == google_uid))
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> User:
        user = User(**data)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, data: dict) -> User:
        for key, value in data.items():
            setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user
