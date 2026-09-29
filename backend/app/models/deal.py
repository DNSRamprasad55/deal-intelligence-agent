import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, String, Text, Float, Numeric, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class DealStage(str, enum.Enum):
    DISCOVERY = "DISCOVERY"
    QUALIFICATION = "QUALIFICATION"
    TECHNICAL_EVALUATION = "TECHNICAL_EVALUATION"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    CLOSED_WON = "CLOSED_WON"
    CLOSED_LOST = "CLOSED_LOST"


class DealStatus(str, enum.Enum):
    OPEN = "OPEN"
    WON = "WON"
    LOST = "LOST"


class Deal(Base):
    __tablename__ = "deals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    stage = Column(Enum(DealStage), default=DealStage.DISCOVERY, nullable=False, index=True)
    value = Column(Numeric(14, 2), default=0.00, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    probability = Column(Float, default=0.20, nullable=False)
    expected_close_date = Column(Date, nullable=True)
    status = Column(Enum(DealStatus), default=DealStatus.OPEN, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    company = relationship("Company", back_populates="deals")
    owner = relationship("User", back_populates="deals")
    interactions = relationship("Interaction", back_populates="deal", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="deal", cascade="all, delete-orphan")
    actions = relationship("DealAction", back_populates="deal", cascade="all, delete-orphan")
    outcomes = relationship("DealOutcome", back_populates="deal", cascade="all, delete-orphan")
