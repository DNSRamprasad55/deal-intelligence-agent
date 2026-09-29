from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.models.deal import DealStage, DealStatus
from app.schemas.company import CompanyResponse
from app.schemas.auth import UserResponse
from app.schemas.interaction import InteractionResponse


class DealCreate(BaseModel):
    company_id: str
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    stage: DealStage = DealStage.DISCOVERY
    value: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = "USD"
    probability: float = Field(default=0.20, ge=0.0, le=1.0)
    expected_close_date: Optional[date] = None
    status: DealStatus = DealStatus.OPEN


class DealUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    stage: Optional[DealStage] = None
    value: Optional[Decimal] = None
    currency: Optional[str] = None
    probability: Optional[float] = None
    expected_close_date: Optional[date] = None
    status: Optional[DealStatus] = None
    owner_id: Optional[str] = None


class DealResponse(BaseModel):
    id: str
    company_id: str
    owner_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    stage: DealStage
    value: Decimal
    currency: str
    probability: float
    expected_close_date: Optional[date] = None
    status: DealStatus
    created_at: datetime
    updated_at: datetime
    company: Optional[CompanyResponse] = None
    owner: Optional[UserResponse] = None
    interactions: List[InteractionResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class DashboardMetricsResponse(BaseModel):
    total_active_deals: int
    open_pipeline_value: Decimal
    won_deals: int
    lost_deals: int
    recent_deals: List[DealResponse]
    recent_interactions: List[InteractionResponse]
