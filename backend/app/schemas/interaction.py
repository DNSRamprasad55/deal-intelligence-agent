from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.interaction import InteractionType


class HindsightStatusDetail(BaseModel):
    status: str
    bank_id: str = "deal-intelligence-global"
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class InteractionCreate(BaseModel):
    contact_id: Optional[str] = None
    type: InteractionType
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    occurred_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class InteractionResponse(BaseModel):
    id: str
    deal_id: str
    contact_id: Optional[str] = None
    type: InteractionType
    title: str
    content: str
    occurred_at: datetime
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    hindsight_memory_status: str = "pending"
    hindsight: Optional[HindsightStatusDetail] = None

    model_config = ConfigDict(from_attributes=True)
