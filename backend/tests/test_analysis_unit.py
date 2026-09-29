import pytest
from unittest.mock import MagicMock, patch
from app.services.intelligence.analysis_service import deal_analysis_service
from app.schemas.intelligence import EvidenceItem
from app.services.hindsight import hindsight_service, HindsightStatus
from app.models.recommendation import RecommendationStatus
from app.core.config import settings


@pytest.mark.asyncio
async def test_analysis_service_unconfigured():
    mock_db = MagicMock()
    mock_deal = MagicMock()
    mock_db.query().filter().first.return_value = mock_deal

    mock_recall = {
        "status": "not_configured",
        "results": []
    }

    with patch("app.services.intelligence.analysis_service.deal_recall_service.execute_recall_for_deal", return_value=MagicMock(status="not_configured")):
        res = await deal_analysis_service.analyze_deal_intelligence(mock_db, "deal-1")
        assert res.status == "not_configured"
        assert "Connect Hindsight" in res.message


@pytest.mark.asyncio
async def test_analysis_service_no_evidence():
    mock_db = MagicMock()
    mock_deal = MagicMock()
    mock_db.query().filter().first.return_value = mock_deal

    mock_recall_obj = MagicMock()
    mock_recall_obj.status = "success"
    mock_recall_obj.results = []

    with patch("app.services.intelligence.analysis_service.deal_recall_service.execute_recall_for_deal", return_value=mock_recall_obj):
        res = await deal_analysis_service.analyze_deal_intelligence(mock_db, "deal-1")
        assert res.status == "no_evidence"
        assert "No relevant historical experience" in res.message


def test_analyze_and_action_api_endpoints(client):
    # Register & Login
    client.post(
        "/api/auth/register",
        json={"name": "Manager User", "email": "mgr_reflect@example.com", "password": "password123", "role": "manager"}
    )
    login_res = client.post(
        "/api/auth/login",
        json={"email": "mgr_reflect@example.com", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create Company & Deal
    comp_res = client.post(
        "/api/companies",
        headers=headers,
        json={"name": "Northstar Client", "industry": "Logistics"}
    )
    company_id = comp_res.json()["id"]

    deal_res = client.post(
        "/api/deals",
        headers=headers,
        json={"company_id": company_id, "name": "Acme CRM Deal", "stage": "NEGOTIATION", "value": "150000.00"}
    )
    deal_id = deal_res.json()["id"]

    # Mock recall and reflect
    mock_recall_obj = MagicMock()
    mock_recall_obj.status = "success"
    mock_recall_obj.results = [
        EvidenceItem(memory_id="mem-1", content="Northstar deal WON using phased rollout", outcome_hint="WON", context="deal:northstar", tags=["won"]),
        EvidenceItem(memory_id="mem-2", content="Beta deal LOST without rollout plan", outcome_hint="LOST", context="deal:beta", tags=["lost"])
    ]

    mock_reflect_res = {
        "status": "success",
        "structured_output": {
            "situation": "Acme CRM deal in Negotiation",
            "observed_pattern": "Phased rollouts resolve migration concerns",
            "risks": ["Migration delay"],
            "recommendation_title": "Schedule Technical Workshop & Phased Rollout",
            "recommendation_description": "Propose phased rollout to resolve timeline concerns.",
            "reasoning": "Northstar succeeded with phased rollout, Beta failed without one.",
            "alternative_actions": ["Offer migration warranty"],
            "unknowns": ["Target cutover date"]
        }
    }

    with patch("app.services.intelligence.analysis_service.deal_recall_service.execute_recall_for_deal", return_value=mock_recall_obj), \
         patch("app.services.intelligence.analysis_service.hindsight_service.reflect_memories", return_value=mock_reflect_res):
        
        res = client.post(f"/api/deals/{deal_id}/intelligence/analyze", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["deal_id"] == deal_id
        assert data["status"] == "success"
        assert data["recommendation_title"] == "Schedule Technical Workshop & Phased Rollout"
        assert len(data["evidence"]) == 2
        assert data["recommendation"]["status"] == "PENDING"
        rec_id = data["recommendation"]["id"]

        # Test Recommendation Action (Accept)
        action_res = client.post(
            f"/api/recommendations/{rec_id}/action",
            headers=headers,
            json={"status": "ACCEPTED"}
        )
        assert action_res.status_code == 200
        assert action_res.json()["status"] == "ACCEPTED"
