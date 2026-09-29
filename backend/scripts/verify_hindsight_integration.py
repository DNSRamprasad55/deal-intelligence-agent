import os
import sys
import asyncio

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.services.hindsight import hindsight_service, get_hindsight_client, HindsightStatus


async def run_real_hindsight_integration_test():
    print("=" * 70)
    print(" Hindsight Cloud Real Integration Verification ")
    print("=" * 70)

    print(f"HINDSIGHT_BASE_URL: {settings.get_hindsight_base_url()}")
    print(f"HINDSIGHT_BANK_ID:  {settings.HINDSIGHT_BANK_ID}")
    
    if not settings.HINDSIGHT_API_KEY:
        print("\n[SKIP] HINDSIGHT_API_KEY is not set in environment or .env file.")
        print("Set HINDSIGHT_API_KEY=<your_key> in backend/.env to run against live Hindsight Cloud.")
        return False

    api_key_masked = settings.HINDSIGHT_API_KEY[:4] + "..." + settings.HINDSIGHT_API_KEY[-4:] if len(settings.HINDSIGHT_API_KEY) > 8 else "***"
    print(f"HINDSIGHT_API_KEY:  {api_key_masked}")

    # 1. Health Status
    print("\n1. Checking Hindsight status...")
    status = await hindsight_service.get_status()
    print(f"   Status: {status.value}")
    if status != HindsightStatus.AVAILABLE:
        print(f"   [FAIL] Hindsight is not AVAILABLE (reported status: {status.value})")
        return False

    # 2. Ensure Memory Bank
    print(f"\n2. Verifying bank '{settings.HINDSIGHT_BANK_ID}' exists or creating it...")
    bank_ok = await hindsight_service.ensure_bank_exists()
    print(f"   Bank Verification: {'Success' if bank_ok else 'Failed'}")
    if not bank_ok:
        print("   [FAIL] Bank verification/creation failed.")
        return False

    # 3. Test RETAIN
    print("\n3. Testing RETAIN operation with real customer experience content...")
    sample_content = (
        "Deal 'Acme CRM Migration' (Company: 'Acme Corporation', Stage: NEGOTIATION, Value: $150000 USD). "
        "Acme Corporation is evaluating our CRM solution against Salesforce. "
        "The customer is concerned about migration time and prefers a phased rollout."
    )
    
    retain_result = await hindsight_service.retain_interaction(
        deal_id="test-deal-acme-1",
        deal_name="Acme CRM Migration",
        company_name="Acme Corporation",
        deal_stage="NEGOTIATION",
        deal_value="150000.00",
        deal_currency="USD",
        interaction_id="test-inter-acme-1",
        interaction_type="MEETING",
        interaction_title="Acme Architecture & Migration Review",
        interaction_content="Acme Corporation is evaluating our CRM solution against Salesforce. The customer is concerned about migration time and prefers a phased rollout."
    )

    print(f"   Retain Result Status: {retain_result.status}")
    print(f"   Retain Bank ID:       {retain_result.bank_id}")
    print(f"   Retain Memory IDs:    {retain_result.memory_ids}")
    if retain_result.message:
        print(f"   Retain Message:       {retain_result.message}")

    if retain_result.status != "stored":
        print(f"   [FAIL] Retain failed with status: {retain_result.status}")
        return False

    # 4. Optional Verification RECALL
    print("\n4. Verification RECALL query against Hindsight Cloud...")
    try:
        client = get_hindsight_client()
        recall_res = client.recall(
            bank_id=settings.HINDSIGHT_BANK_ID,
            query="What does Acme care about regarding migration?"
        )
        print("   Recall Succeeded!")
        print(f"   Recall Response Summary / Content: {str(recall_res)[:300]}...")
    except Exception as e:
        print(f"   Recall verification warning: {str(e)}")

    print("\n" + "=" * 70)
    print(" REAL HINDSIGHT CLOUD INTEGRATION SUCCESSFUL ")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = asyncio.run(run_real_hindsight_integration_test())
    sys.exit(0 if success else 1)
