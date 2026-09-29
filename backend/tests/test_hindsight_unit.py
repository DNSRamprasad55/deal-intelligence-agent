import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.hindsight import HindsightService, HindsightStatus, hindsight_service
from app.core.config import settings


@pytest.mark.asyncio
async def test_hindsight_status_not_configured():
    with patch.object(settings, "HINDSIGHT_API_KEY", None):
        status = await hindsight_service.get_status()
        assert status == HindsightStatus.NOT_CONFIGURED


@pytest.mark.asyncio
async def test_hindsight_status_available():
    mock_client = MagicMock()
    mock_client.aget_version = AsyncMock(return_value={"version": "0.10.1"})

    with patch("app.services.hindsight.service.get_hindsight_client", return_value=mock_client), \
         patch.object(settings, "HINDSIGHT_API_KEY", "test-api-key"):
        status = await hindsight_service.get_status()
        assert status == HindsightStatus.AVAILABLE
        mock_client.aget_version.assert_called_once()


@pytest.mark.asyncio
async def test_hindsight_status_unavailable():
    mock_client = MagicMock()
    mock_client.aget_version = AsyncMock(side_effect=Exception("Connection timeout"))

    with patch("app.services.hindsight.service.get_hindsight_client", return_value=mock_client), \
         patch.object(settings, "HINDSIGHT_API_KEY", "test-api-key"):
        status = await hindsight_service.get_status()
        assert status == HindsightStatus.UNAVAILABLE


def test_build_interaction_memory_content():
    service = HindsightService()
    content = service.build_interaction_memory_content(
        deal_name="Acme License Expansion",
        company_name="Acme Corp",
        deal_stage="NEGOTIATION",
        deal_value="150000.00",
        deal_currency="USD",
        interaction_type="MEETING",
        interaction_title="Security Review",
        interaction_content="Customer raised migration concerns compared with Salesforce.",
        contact_name="John Doe"
    )

    assert "Acme License Expansion" in content
    assert "Acme Corp" in content
    assert "NEGOTIATION" in content
    assert "Security Review" in content
    assert "Salesforce" in content
    assert "John Doe" in content


@pytest.mark.asyncio
async def test_retain_interaction_with_mock_sdk():
    service = HindsightService()
    mock_client = MagicMock()
    mock_res = MagicMock()
    mock_res.id = "memory-12345"
    mock_client.aretain = AsyncMock(return_value=mock_res)
    mock_client.aget_version = AsyncMock(return_value={"version": "0.10.1"})

    with patch("app.services.hindsight.service.get_hindsight_client", return_value=mock_client), \
         patch.object(settings, "HINDSIGHT_API_KEY", "valid-key"):
        
        result = await service.retain_interaction(
            deal_id="deal-1",
            deal_name="Acme Deal",
            company_name="Acme Corp",
            deal_stage="PROPOSAL",
            deal_value="100000",
            deal_currency="USD",
            interaction_id="inter-1",
            interaction_type="CALL",
            interaction_title="Discovery Call",
            interaction_content="Client asked about migration timelines."
        )

        assert result.status == "stored"
        assert result.bank_id == service.bank_id
        assert "memory-12345" in result.memory_ids
        mock_client.aretain.assert_called_once()


@pytest.mark.asyncio
async def test_retain_interaction_hindsight_failure_handling():
    service = HindsightService()
    mock_client = MagicMock()
    mock_client.aretain = AsyncMock(side_effect=Exception("Hindsight API server 500 error"))
    mock_client.aget_version = AsyncMock(return_value={"version": "0.10.1"})

    with patch("app.services.hindsight.service.get_hindsight_client", return_value=mock_client), \
         patch.object(settings, "HINDSIGHT_API_KEY", "valid-key"):
        
        result = await service.retain_interaction(
            deal_id="deal-2",
            deal_name="Beta Deal",
            company_name="Beta Inc",
            deal_stage="QUALIFICATION",
            deal_value="50000",
            deal_currency="USD",
            interaction_id="inter-2",
            interaction_type="EMAIL",
            interaction_title="Follow-up Email",
            interaction_content="Sent migration proposal document."
        )

        assert result.status == "error"
        assert "500 error" in result.message
