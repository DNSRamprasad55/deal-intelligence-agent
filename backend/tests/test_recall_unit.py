import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.intelligence.recall_service import deal_recall_service
from app.services.hindsight import hindsight_service, HindsightStatus
from app.core.config import settings


def test_query_generation_custom_and_default():
    mock_company = MagicMock()
    mock_company.name = "Acme Corp"
    mock_company.industry = "Enterprise SaaS"

    mock_deal = MagicMock()
    mock_deal.name = "Acme Enterprise License"
    mock_deal.company = mock_company
    mock_deal.stage = "NEGOTIATION"
    mock_deal.interactions = []
    mock_deal.description = "Acme migration requirements"

    # Custom query
    custom_q = deal_recall_service.build_deal_intelligence_query(mock_deal, "Custom search query")
    assert custom_q == "Custom search query"

    # Default generated query
    gen_q = deal_recall_service.build_deal_intelligence_query(mock_deal, None)
    assert "Acme Enterprise License" in gen_q
    assert "Acme Corp" in gen_q
    assert "Enterprise SaaS" in gen_q
    assert "NEGOTIATION" in gen_q
    assert "migration" in gen_q


def test_detect_outcome_hint():
    assert deal_recall_service.detect_outcome_hint("Deal was WON after workshop", []) == "WON"
    assert deal_recall_service.detect_outcome_hint("Deal was LOST due to delay", []) == "LOST"
    assert deal_recall_service.detect_outcome_hint("Some memory text", ["stage:closed_won"]) == "WON"
    assert deal_recall_service.detect_outcome_hint("Some memory text", ["lost"]) == "LOST"
    assert deal_recall_service.detect_outcome_hint("Random text", ["other"]) == "UNKNOWN"


@pytest.mark.asyncio
async def test_hindsight_service_recall_mock():
    mock_client = MagicMock()
    mock_result_1 = MagicMock()
    mock_result_1.id = "mem-1"
    mock_result_1.text = "Northstar migration concern was WON using phased rollout"
    mock_result_1.type = "GENERAL_EXPERIENCE"
    mock_result_1.context = "deal:northstar-1"
    mock_result_1.metadata = {"company": "Northstar"}
    mock_result_1.tags = ["won", "stage:closed_won"]
    mock_result_1.document_id = "doc-1"

    mock_recall_resp = MagicMock()
    mock_recall_resp.results = [mock_result_1]
    mock_client.arecall = AsyncMock(return_value=mock_recall_resp)
    mock_client.recall.return_value = mock_recall_resp
    mock_client.aget_version = AsyncMock(return_value={"version": "0.10.1"})

    with patch("app.services.hindsight.service.get_hindsight_client", return_value=mock_client), \
         patch.object(settings, "HINDSIGHT_API_KEY", "valid-key"):
        
        res = await hindsight_service.recall_memories("Find migration deals")
        assert res["status"] == "success"
        assert res["count"] == 1
        assert res["results"][0]["id"] == "mem-1"
        assert "Northstar" in res["results"][0]["content"]


@pytest.mark.asyncio
async def test_hindsight_service_recall_unavailable():
    with patch.object(settings, "HINDSIGHT_API_KEY", None):
        res = await hindsight_service.recall_memories("Find migration deals")
        assert res["status"] == "not_configured"
        assert res["results"] == []


def test_recall_api_endpoint(client):
    # Register & Login
    client.post(
        "/api/auth/register",
        json={"name": "Rep User", "email": "recall_user@example.com", "password": "password123"}
    )
    login_res = client.post(
        "/api/auth/login",
        json={"email": "recall_user@example.com", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create Company & Deal
    comp_res = client.post(
        "/api/companies",
        headers=headers,
        json={"name": "Test Company", "industry": "Software"}
    )
    company_id = comp_res.json()["id"]

    deal_res = client.post(
        "/api/deals",
        headers=headers,
        json={"company_id": company_id, "name": "Migration Deal", "stage": "PROPOSAL"}
    )
    deal_id = deal_res.json()["id"]

    # Trigger recall endpoint
    mock_recall_response = {
        "status": "success",
        "bank_id": "deal-intelligence-global",
        "query": "Migration query",
        "results": [
            {
                "id": "mem-northstar",
                "content": "Northstar deal WON with phased migration rollout.",
                "context": "deal:northstar",
                "type": "GENERAL_EXPERIENCE",
                "metadata": {"company": "Northstar"},
                "tags": ["won"]
            },
            {
                "id": "mem-beta",
                "content": "Beta deal LOST due to lack of concrete migration timeline.",
                "context": "deal:beta",
                "type": "GENERAL_EXPERIENCE",
                "metadata": {"company": "Beta"},
                "tags": ["lost"]
            }
        ],
        "count": 2
    }

    with patch("app.services.intelligence.recall_service.hindsight_service.recall_memories", return_value=mock_recall_response):
        res = client.post(
            f"/api/deals/{deal_id}/intelligence/recall",
            headers=headers,
            json={"limit": 5}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["deal_id"] == deal_id
        assert data["count"] == 2
        assert data["results"][0]["outcome_hint"] == "WON"
        assert data["results"][1]["outcome_hint"] == "LOST"
