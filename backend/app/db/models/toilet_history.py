import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base


class ToiletHistory(Base):
    __tablename__ = "toilet_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    toilet_id = Column(UUID(as_uuid=True), ForeignKey("toilets.id", ondelete="CASCADE"), nullable=False)
    snapshot = Column(JSONB, nullable=False)
    changed_fields = Column(ARRAY(Text), nullable=True)
    change_type = Column(String(20), nullable=False)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    toilet = relationship("Toilet", back_populates="history")
