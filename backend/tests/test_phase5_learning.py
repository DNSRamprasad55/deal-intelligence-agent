import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.database import get_db
from app.models.company import Company
from app.models.deal import Deal, DealStage, DealStatus
from app.models.recommendation import Recommendation, RecommendationStatus
from app.models.deal_action import DealAction
from app.models.deal_outcome import DealOutcome, OutcomeType
from app.services.hindsight.models import HindsightMemoryStatus
from app.services.intelligence.analysis_service import deal_analysis_service
from app.schemas.intelligence import CreateOutcomePayload


@pytest.fixture
def sample_deal_data(db_session: Session):
    company = Company(name="Test Learning Corp", industry="Enterprise Tech")
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)

    deal = Deal(
        company_id=company.id,
        name="Acme Migration Learning Deal",
        description="Migration deal for testing outcome retain loop",
        stage=DealStage.NEGOTIATION,
        value=150000.00,
        currency="USD",
        probability=0.75,
        status=DealStatus.OPEN
    )
    db_session.add(deal)
    db_session.commit()
    db_session.refresh(deal)

    rec = Recommendation(
        deal_id=deal.id,
        title="Schedule Technical Migration Workshop & Propose Phased Rollout Plan",
        description="Proactively address customer migration concerns by organizing an architecture workshop.",
        reasoning="Historical evidence shows phased rollout plans resolve timeline concerns.",
        confidence=0.85,
        status=RecommendationStatus.PENDING
    )
    db_session.add(rec)
    db_session.commit()
    db_session.refresh(rec)

    return {"company": company, "deal": deal, "recommendation": rec}


def test_recommendation_acceptance(db_session: Session, sample_deal_data):
    rec = sample_deal_data["recommendation"]
    
    rec_res = deal_analysis_service.update_recommendation_status(
        db=db_session,
        recommendation_id=rec.id,
        new_status=RecommendationStatus.ACCEPTED
    )

    assert rec_res.status == RecommendationStatus.ACCEPTED
    assert rec_res.action_id is not None

    action = db_session.query(DealAction).filter(DealAction.id == rec_res.action_id).first()
    assert action is not None
    assert action.deal_id == rec.deal_id
    assert action.recommendation_id == rec.id
    assert action.status == "COMPLETED"


def test_recommendation_rejection(db_session: Session, sample_deal_data):
    rec = sample_deal_data["recommendation"]

    rec_res = deal_analysis_service.update_recommendation_status(
        db=db_session,
        recommendation_id=rec.id,
        new_status=RecommendationStatus.REJECTED
    )

    assert rec_res.status == RecommendationStatus.REJECTED
    assert rec_res.action_id is None

    action_count = db_session.query(DealAction).filter(DealAction.recommendation_id == rec.id).count()
    assert action_count == 0


@pytest.mark.asyncio
async def test_outcome_creation_and_hindsight_retain(db_session: Session, sample_deal_data):
    rec = sample_deal_data["recommendation"]
    deal = sample_deal_data["deal"]

    # 1. Accept recommendation to create Action
    rec_res = deal_analysis_service.update_recommendation_status(
        db=db_session,
        recommendation_id=rec.id,
        new_status=RecommendationStatus.ACCEPTED
    )
    action_id = rec_res.action_id

    # 2. Record outcome with mocked Hindsight RETAIN service
    mock_hindsight_status = HindsightMemoryStatus(
        status="stored",
        bank_id="deal-intelligence-global",
        memory_ids=["mem-outcome-123"]
    )

    with patch("app.services.intelligence.analysis_service.hindsight_service.retain_outcome", new_callable=AsyncMock) as mock_retain:
        mock_retain.return_value = mock_hindsight_status

        payload = CreateOutcomePayload(
            outcome_type=OutcomeType.POSITIVE,
            description="Customer accepted the phased rollout proposal and continued the deal.",
            impact="Reduced migration concern and moved deal toward proposal."
        )

        outcome_res = await deal_analysis_service.record_action_outcome(
            db=db_session,
            action_id=action_id,
            payload=payload
        )

        # 3. Assert PostgreSQL state
        assert outcome_res.id is not None
        assert outcome_res.action_id == action_id
        assert outcome_res.deal_id == deal.id
        assert outcome_res.outcome_type == OutcomeType.POSITIVE
        assert outcome_res.hindsight.status == "stored"
        assert outcome_res.hindsight.bank_id == "deal-intelligence-global"

        db_outcome = db_session.query(DealOutcome).filter(DealOutcome.id == outcome_res.id).first()
        assert db_outcome is not None
        assert db_outcome.description == payload.description

        # Assert mock call parameters
        mock_retain.assert_called_once()
        call_kwargs = mock_retain.call_args.kwargs
        assert call_kwargs["deal_id"] == deal.id
        assert call_kwargs["outcome_type"] == "POSITIVE"


@pytest.mark.asyncio
async def test_hindsight_failure_resilience(db_session: Session, sample_deal_data):
    rec = sample_deal_data["recommendation"]

    rec_res = deal_analysis_service.update_recommendation_status(
        db=db_session,
        recommendation_id=rec.id,
        new_status=RecommendationStatus.ACCEPTED
    )
    action_id = rec_res.action_id

    # Mock Hindsight service failure/unavailability
    mock_hindsight_status = HindsightMemoryStatus(
        status="unavailable",
        bank_id="deal-intelligence-global",
        message="Hindsight Cloud unreachable"
    )

    with patch("app.services.intelligence.analysis_service.hindsight_service.retain_outcome", new_callable=AsyncMock) as mock_retain:
        mock_retain.return_value = mock_hindsight_status

        payload = CreateOutcomePayload(
            outcome_type=OutcomeType.POSITIVE,
            description="Phased rollout accepted despite memory service being down.",
            impact="Deal advanced."
        )

        outcome_res = await deal_analysis_service.record_action_outcome(
            db=db_session,
            action_id=action_id,
            payload=payload
        )

        # Database state MUST still be saved
        assert outcome_res.id is not None
        assert outcome_res.hindsight.status == "unavailable"

        db_outcome = db_session.query(DealOutcome).filter(DealOutcome.id == outcome_res.id).first()
        assert db_outcome is not None
