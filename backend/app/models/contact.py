import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    role_in_deal = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    company = relationship("Company", back_populates="contacts")
    interactions = relationship("Interaction", back_populates="contact")
