from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class HindsightStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_CONFIGURED = "NOT_CONFIGURED"


class MemoryType(str, Enum):
    CUSTOMER_FACT = "CUSTOMER_FACT"
    OBJECTION = "OBJECTION"
    COMPETITOR = "COMPETITOR"
    STAKEHOLDER = "STAKEHOLDER"
    REQUIREMENT = "REQUIREMENT"
    COMMITMENT = "COMMITMENT"
    DECISION = "DECISION"
    ACTION = "ACTION"
    OUTCOME = "OUTCOME"
    GENERAL_EXPERIENCE = "GENERAL_EXPERIENCE"


class MemoryItem(BaseModel):
    memory_type: MemoryType
    deal_id: str
    company_id: Optional[str] = None
    content: str
    source_type: str = "interaction"
    source_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class HindsightMemoryStatus(BaseModel):
    status: str  # "stored", "not_configured", "unavailable", "error"
    bank_id: str
    memory_ids: List[str] = Field(default_factory=list)
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
