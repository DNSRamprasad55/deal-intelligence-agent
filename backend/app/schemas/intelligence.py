from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.models.recommendation import RecommendationStatus


class RecallRequestPayload(BaseModel):
    query: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)


class EvidenceItem(BaseModel):
    memory_id: str
    content: str
    context: Optional[str] = None
    type: Optional[str] = "GENERAL_EXPERIENCE"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    outcome_hint: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DealRecallResponse(BaseModel):
    deal_id: str
    query: str
    results: List[EvidenceItem] = Field(default_factory=list)
    count: int = 0
    status: str  # "success", "not_configured", "unavailable", "error"
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


from app.models.deal_outcome import OutcomeType


class RecommendationActionPayload(BaseModel):
    status: RecommendationStatus


class RecommendationResponse(BaseModel):
    id: str
    deal_id: str
    title: str
    description: str
    reasoning: Optional[str] = None
    confidence: float = 0.0
    status: RecommendationStatus
    action_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreateOutcomePayload(BaseModel):
    outcome_type: OutcomeType
    description: str
    impact: Optional[str] = None


class HindsightStatusInfo(BaseModel):
    status: str  # "stored", "unavailable", "not_configured", "error"
    bank_id: Optional[str] = None
    message: Optional[str] = None


class OutcomeResponse(BaseModel):
    id: str
    action_id: Optional[str] = None
    deal_id: str
    recommendation_id: Optional[str] = None
    outcome_type: OutcomeType
    description: str
    impact: Optional[str] = None
    hindsight: HindsightStatusInfo
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DealAnalysisResponse(BaseModel):
    deal_id: str
    recommendation: Optional[RecommendationResponse] = None
    situation: str = ""
    observed_pattern: str = ""
    risks: List[str] = Field(default_factory=list)
    recommendation_title: str = ""
    recommendation_description: str = ""
    reasoning: str = ""
    alternative_actions: List[str] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    status: str  # "success", "no_evidence", "not_configured", "unavailable", "error"
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
