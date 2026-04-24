from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException
from app.db.session import get_db
from app.repositories.user_repository import UserRepository


async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException("인증 헤더 형식이 잘못되었습니다.")
    token = authorization[7:]
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise UnauthorizedException("Access 토큰이 아닙니다.")
    user_id = payload.get("sub")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise UnauthorizedException("유효하지 않은 사용자입니다.")
    return user


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    if not authorization:
        return None
    try:
        return await get_current_user(authorization, db)
    except Exception:
        return None
