import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base


class UserRole(str, enum.Enum):
    SALES_REP = "sales_rep"
    MANAGER = "manager"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.SALES_REP, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    deals = relationship("Deal", back_populates="owner")
    interactions = relationship("Interaction", back_populates="author")
