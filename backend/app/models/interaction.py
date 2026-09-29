import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class InteractionType(str, enum.Enum):
    CALL = "CALL"
    MEETING = "MEETING"
    EMAIL = "EMAIL"
    NOTE = "NOTE"
    DEMO = "DEMO"
    TECHNICAL_REVIEW = "TECHNICAL_REVIEW"


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    deal_id = Column(String(36), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(String(36), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True)
    type = Column(Enum(InteractionType), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    occurred_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    deal = relationship("Deal", back_populates="interactions")
    contact = relationship("Contact", back_populates="interactions")
    author = relationship("User", back_populates="interactions")
