import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class DealAction(Base):
    __tablename__ = "deal_actions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    deal_id = Column(String(36), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True)
    recommendation_id = Column(String(36), ForeignKey("recommendations.id", ondelete="SET NULL"), nullable=True)
    action_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="PENDING", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    deal = relationship("Deal", back_populates="actions")
    recommendation = relationship("Recommendation", back_populates="actions")
    outcome = relationship("DealOutcome", back_populates="action", uselist=False)
