import uuid
from datetime import datetime
from sqlalchemy import Column, Text, SmallInteger, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class ToiletPhoto(Base):
    __tablename__ = "toilet_photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    toilet_id = Column(UUID(as_uuid=True), ForeignKey("toilets.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(Text, nullable=False)
    storage_path = Column(Text, nullable=False)
    display_order = Column(SmallInteger, nullable=False, default=0)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    toilet = relationship("Toilet", back_populates="photos")
