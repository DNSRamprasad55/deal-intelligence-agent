import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    industry = Column(String(255), nullable=True)
    size = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="company", cascade="all, delete-orphan")
