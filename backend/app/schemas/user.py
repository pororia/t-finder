from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserResponse(BaseModel):
    id: UUID
    email: str
    nickname: str
    profile_image_url: Optional[str]
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
