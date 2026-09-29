from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.intelligence import (
    DealRecallResponse,
    DealAnalysisResponse,
    RecallRequestPayload,
    RecommendationResponse,
    RecommendationActionPayload,
    CreateOutcomePayload,
    OutcomeResponse
)
from app.services.intelligence.recall_service import deal_recall_service
from app.services.intelligence.analysis_service import deal_analysis_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(tags=["intelligence"])


@router.post("/deals/{deal_id}/intelligence/recall", response_model=DealRecallResponse)
async def recall_deal_intelligence(
    deal_id: str,
    payload: Optional[RecallRequestPayload] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await deal_recall_service.execute_recall_for_deal(
        db=db,
        deal_id=deal_id,
        payload=payload
    )


@router.post("/deals/{deal_id}/intelligence/analyze", response_model=DealAnalysisResponse)
async def analyze_deal_intelligence(
    deal_id: str,
    payload: Optional[RecallRequestPayload] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await deal_analysis_service.analyze_deal_intelligence(
        db=db,
        deal_id=deal_id,
        payload=payload
    )


@router.post("/recommendations/{recommendation_id}/action", response_model=RecommendationResponse)
def act_on_recommendation(
    recommendation_id: str,
    action: RecommendationActionPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return deal_analysis_service.update_recommendation_status(
        db=db,
        recommendation_id=recommendation_id,
        new_status=action.status
    )


@router.post("/actions/{action_id}/outcome", response_model=OutcomeResponse)
async def record_action_outcome(
    action_id: str,
    payload: CreateOutcomePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await deal_analysis_service.record_action_outcome(
        db=db,
        action_id=action_id,
        payload=payload
    )
