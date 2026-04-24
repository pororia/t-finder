from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import GoogleLoginRequest, LoginResponse
from app.schemas.common import APIResponse
from app.core.dependencies import get_current_user
from app.schemas.user import UserResponse

router = APIRouter()


@router.post("/google", response_model=APIResponse[LoginResponse])
async def google_login(request: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.login_with_google(request.id_token)
    return APIResponse.ok(result)


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(
    authorization: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db),
):
    from fastapi import Header
    from app.core.security import decode_token
    # handled via dependency
    return APIResponse.ok({"message": "use Authorization header with refresh token"})


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_me(current_user=Depends(get_current_user)):
    return APIResponse.ok(current_user)


@router.post("/logout", response_model=APIResponse)
async def logout(current_user=Depends(get_current_user)):
    return APIResponse.ok({"message": "로그아웃 되었습니다."})
