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


class Toilet(Base):
    __tablename__ = "toilets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    address = Column(String(500), nullable=False)
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
    payment_type = Column(Enum(PaymentType), nullable=False, default=PaymentType.FREE)
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
