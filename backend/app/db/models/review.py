import uuid
from datetime import datetime
from sqlalchemy import Column, SmallInteger, Text, ForeignKey, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    toilet_id = Column(UUID(as_uuid=True), ForeignKey("toilets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = Column(SmallInteger, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    toilet = relationship("Toilet", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    __table_args__ = (
        UniqueConstraint("toilet_id", "user_id", name="uq_review_toilet_user"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="chk_rating"),
    )
