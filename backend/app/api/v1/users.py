from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.schemas.common import APIResponse
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_my_profile(current_user=Depends(get_current_user)):
    return APIResponse.ok(current_user)
