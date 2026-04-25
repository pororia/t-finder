from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class LocationSchema(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class ToiletCreate(BaseModel):
    location: LocationSchema
    address: str = Field(..., max_length=500)
    address_detail: Optional[str] = Field(None, max_length=200)
    name: Optional[str] = Field(None, max_length=200)
    cleanliness: int = Field(..., ge=1, le=5)
    description: Optional[str] = None
    has_password: bool = False
    password_value: Optional[str] = None
    is_unisex: bool = False
    is_accessible: bool = False
    seat_count: int = Field(0, ge=0)
    urinal_count: int = Field(0, ge=0)
    male_seat_count: int = Field(0, ge=0)
    male_urinal_count: int = Field(0, ge=0)
    female_seat_count: int = Field(0, ge=0)
    payment_type: str = Field("FREE", pattern="^(FREE|PAID)$")
    cost: Optional[int] = Field(None, ge=0)

    @model_validator(mode="after")
    def validate_password_and_cost(self):
        if self.has_password and not self.password_value:
            raise ValueError("비밀번호가 있다고 표시한 경우 비밀번호 값을 입력해야 합니다.")
        if self.payment_type == "PAID" and self.cost is None:
            raise ValueError("유료 화장실은 비용을 입력해야 합니다.")
        return self


class ToiletUpdate(BaseModel):
    address: Optional[str] = Field(None, max_length=500)
    address_detail: Optional[str] = Field(None, max_length=200)
    name: Optional[str] = Field(None, max_length=200)
    cleanliness: Optional[int] = Field(None, ge=1, le=5)
    description: Optional[str] = None
    has_password: Optional[bool] = None
    password_value: Optional[str] = None
    is_unisex: Optional[bool] = None
    is_accessible: Optional[bool] = None
    seat_count: Optional[int] = Field(None, ge=0)
    urinal_count: Optional[int] = Field(None, ge=0)
    male_seat_count: Optional[int] = Field(None, ge=0)
    male_urinal_count: Optional[int] = Field(None, ge=0)
    female_seat_count: Optional[int] = Field(None, ge=0)
    payment_type: Optional[str] = Field(None, pattern="^(FREE|PAID)$")
    cost: Optional[int] = Field(None, ge=0)


class PhotoInfo(BaseModel):
    id: UUID
    image_url: str
    display_order: int

    class Config:
        from_attributes = True


class ToiletResponse(BaseModel):
    id: UUID
    location: LocationSchema
    address: str
    address_detail: Optional[str]
    name: Optional[str]
    cleanliness: int
    description: Optional[str]
    has_password: bool
    password_value: Optional[str] = None
    is_unisex: bool
    is_accessible: bool
    seat_count: int
    urinal_count: int
    male_seat_count: int = 0
    male_urinal_count: int = 0
    female_seat_count: int = 0
    payment_type: str
    cost: Optional[int]
    photos: List[PhotoInfo] = []
    avg_rating: Optional[float] = None
    review_count: int = 0
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ToiletNearbyResponse(BaseModel):
    id: UUID
    address: str
    location: LocationSchema
    cleanliness: int
    is_unisex: bool
    is_accessible: bool
    payment_type: str
    cost: Optional[int]
    has_password: bool
    thumbnail_url: Optional[str]
    distance_m: float


class ToiletHistoryResponse(BaseModel):
    id: UUID
    toilet_id: UUID
    snapshot: dict
    changed_fields: Optional[List[str]]
    change_type: str
    changed_by: UUID
    changed_at: datetime

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: UUID
    toilet_id: UUID
    user_id: UUID
    rating: int
    comment: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
