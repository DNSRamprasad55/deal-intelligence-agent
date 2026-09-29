import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class OutcomeType(str, enum.Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class DealOutcome(Base):
    __tablename__ = "deal_outcomes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    deal_id = Column(String(36), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True)
    recommendation_id = Column(String(36), ForeignKey("recommendations.id", ondelete="SET NULL"), nullable=True)
    action_id = Column(String(36), ForeignKey("deal_actions.id", ondelete="SET NULL"), nullable=True)
    outcome_type = Column(Enum(OutcomeType), nullable=False)
    description = Column(Text, nullable=False)
    impact = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    deal = relationship("Deal", back_populates="outcomes")
    recommendation = relationship("Recommendation", back_populates="outcomes")
    action = relationship("DealAction", back_populates="outcome")
