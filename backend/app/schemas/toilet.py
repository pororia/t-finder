from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import re


class LocationSchema(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class ToiletCreate(BaseModel):
    toilet_type: Optional[str] = Field(None, pattern="^(간이|개방|공중|이동)$")
    location: LocationSchema
    address: str = Field(..., max_length=500)
    address_jibun: Optional[str] = Field(None, max_length=500)
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
    male_disabled_seat_count: int = Field(0, ge=0)
    male_disabled_urinal_count: int = Field(0, ge=0)
    male_children_seat_count: int = Field(0, ge=0)
    male_children_urinal_count: int = Field(0, ge=0)
    female_seat_count: int = Field(0, ge=0)
    female_disabled_seat_count: int = Field(0, ge=0)
    female_children_seat_count: int = Field(0, ge=0)
    open_hours: Optional[str] = Field(None, max_length=200)
    has_emergency_bell: bool = False
    emergency_bell_location: Optional[str] = Field(None, max_length=200)
    has_entrance_cctv: bool = False
    has_diaper_table: bool = False
    diaper_table_location: Optional[str] = Field(None, max_length=200)
    remodeling_date: Optional[str] = Field(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
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
    toilet_type: Optional[str] = Field(None, pattern="^(간이|개방|공중|이동)$")
    address: Optional[str] = Field(None, max_length=500)
    address_jibun: Optional[str] = Field(None, max_length=500)
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
    male_disabled_seat_count: Optional[int] = Field(None, ge=0)
    male_disabled_urinal_count: Optional[int] = Field(None, ge=0)
    male_children_seat_count: Optional[int] = Field(None, ge=0)
    male_children_urinal_count: Optional[int] = Field(None, ge=0)
    female_seat_count: Optional[int] = Field(None, ge=0)
    female_disabled_seat_count: Optional[int] = Field(None, ge=0)
    female_children_seat_count: Optional[int] = Field(None, ge=0)
    open_hours: Optional[str] = Field(None, max_length=200)
    has_emergency_bell: Optional[bool] = None
    emergency_bell_location: Optional[str] = Field(None, max_length=200)
    has_entrance_cctv: Optional[bool] = None
    has_diaper_table: Optional[bool] = None
    diaper_table_location: Optional[str] = Field(None, max_length=200)
    remodeling_date: Optional[str] = Field(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
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
    toilet_type: Optional[str] = None
    location: LocationSchema
    address: str
    address_jibun: Optional[str] = None
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
    male_disabled_seat_count: int = 0
    male_disabled_urinal_count: int = 0
    male_children_seat_count: int = 0
    male_children_urinal_count: int = 0
    female_seat_count: int = 0
    female_disabled_seat_count: int = 0
    female_children_seat_count: int = 0
    open_hours: Optional[str] = None
    has_emergency_bell: bool = False
    emergency_bell_location: Optional[str] = None
    has_entrance_cctv: bool = False
    has_diaper_table: bool = False
    diaper_table_location: Optional[str] = None
    remodeling_date: Optional[str] = None
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
