import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, String, Text, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class RecommendationStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    deal_id = Column(String(36), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    reasoning = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0, nullable=False)
    status = Column(Enum(RecommendationStatus), default=RecommendationStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    deal = relationship("Deal", back_populates="recommendations")
    actions = relationship("DealAction", back_populates="recommendation")
    outcomes = relationship("DealOutcome", back_populates="recommendation")
