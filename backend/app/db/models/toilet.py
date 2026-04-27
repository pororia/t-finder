import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, SmallInteger, Boolean, Integer, Text, ForeignKey, DateTime, Enum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from app.db.base import Base


class PaymentType(str, enum.Enum):
    FREE = "FREE"
    PAID = "PAID"


class ToiletType(str, enum.Enum):
    SIMPLE = "간이"
    OPEN = "개방"
    PUBLIC = "공중"
    MOBILE = "이동"


class Toilet(Base):
    __tablename__ = "toilets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    toilet_type = Column(Enum(ToiletType, name="toilet_type", create_type=False), nullable=True)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    address = Column(String(500), nullable=False)
    address_jibun = Column(String(500), nullable=True)
    address_detail = Column(String(200), nullable=True)
    name = Column(String(200), nullable=True)
    cleanliness = Column(SmallInteger, nullable=False)
    description = Column(Text, nullable=True)
    has_password = Column(Boolean, nullable=False, default=False)
    password_value = Column(String(100), nullable=True)
    is_unisex = Column(Boolean, nullable=False, default=False)
    is_accessible = Column(Boolean, nullable=False, default=False)
    seat_count = Column(SmallInteger, nullable=False, default=0)
    urinal_count = Column(SmallInteger, nullable=False, default=0)
    male_seat_count = Column(SmallInteger, nullable=False, default=0)
    male_urinal_count = Column(SmallInteger, nullable=False, default=0)
    male_disabled_seat_count = Column(SmallInteger, nullable=False, default=0)
    male_disabled_urinal_count = Column(SmallInteger, nullable=False, default=0)
    male_children_seat_count = Column(SmallInteger, nullable=False, default=0)
    male_children_urinal_count = Column(SmallInteger, nullable=False, default=0)
    female_seat_count = Column(SmallInteger, nullable=False, default=0)
    female_disabled_seat_count = Column(SmallInteger, nullable=False, default=0)
    female_children_seat_count = Column(SmallInteger, nullable=False, default=0)
    open_hours = Column(String(200), nullable=True)
    has_emergency_bell = Column(Boolean, nullable=False, default=False)
    emergency_bell_location = Column(String(200), nullable=True)
    has_entrance_cctv = Column(Boolean, nullable=False, default=False)
    has_diaper_table = Column(Boolean, nullable=False, default=False)
    diaper_table_location = Column(String(200), nullable=True)
    remodeling_date = Column(String(7), nullable=True)
    payment_type = Column(Enum(PaymentType, name="payment_type", create_type=False), nullable=False, default=PaymentType.FREE)
    cost = Column(Integer, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    creator = relationship("User", back_populates="toilets")
    photos = relationship("ToiletPhoto", back_populates="toilet", cascade="all, delete-orphan")
    history = relationship("ToiletHistory", back_populates="toilet", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="toilet", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("cleanliness BETWEEN 1 AND 5", name="chk_cleanliness"),
        CheckConstraint("seat_count >= 0", name="chk_seat_count"),
        CheckConstraint("urinal_count >= 0", name="chk_urinal_count"),
    )
