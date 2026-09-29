import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.services.hindsight import hindsight_service, HindsightStatus


async def run_phase3_real_recall_test():
    print("=" * 70)
    print(" Phase 3 Real Hindsight Cloud RECALL Verification ")
    print("=" * 70)

    print(f"HINDSIGHT_BASE_URL: {settings.get_hindsight_base_url()}")
    print(f"HINDSIGHT_BANK_ID:  {settings.HINDSIGHT_BANK_ID}")

    if not settings.HINDSIGHT_API_KEY:
        print("\n[SKIP] HINDSIGHT_API_KEY is not set in environment or .env file.")
        print("Set HINDSIGHT_API_KEY=<your_key> in backend/.env to run against live Hindsight Cloud.")
        return False

    # 1. Health Status
    print("\n1. Checking Hindsight status...")
    status = await hindsight_service.get_status()
    print(f"   Status: {status.value}")
    if status != HindsightStatus.AVAILABLE:
        print(f"   [FAIL] Hindsight is not AVAILABLE (reported status: {status.value})")
        return False

    # 2. Seed Historical Experiences (Northstar WON & Beta LOST & Acme Current)
    print("\n2. Seeding historical deal experiences into Hindsight Cloud...")

    experiences = [
        {
            "deal_id": "demo-northstar-won",
            "deal_name": "Northstar Systems CRM Migration",
            "company": "Northstar Systems",
            "stage": "CLOSED_WON",
            "value": "180000.00",
            "currency": "USD",
            "inter_id": "inter-northstar-1",
            "type": "TECHNICAL_REVIEW",
            "title": "Migration Workshop & Phased Rollout Plan",
            "content": "Northstar was concerned about migration time. The team proposed a phased rollout and conducted a technical migration workshop. The deal was eventually won."
        },
        {
            "deal_id": "demo-beta-lost",
            "deal_name": "Beta Cloud Expansion",
            "company": "Beta Logistics",
            "stage": "CLOSED_LOST",
            "value": "120000.00",
            "currency": "USD",
            "inter_id": "inter-beta-1",
            "type": "MEETING",
            "title": "Migration Timeline Discussion",
            "content": "Beta had the same migration concern, but no concrete migration plan was provided. The deal was eventually lost."
        },
        {
            "deal_id": "demo-acme-current",
            "deal_name": "Acme CRM Migration",
            "company": "Acme Corporation",
            "stage": "NEGOTIATION",
            "value": "150000.00",
            "currency": "USD",
            "inter_id": "inter-acme-1",
            "type": "MEETING",
            "title": "Salesforce Comparison & Migration Timeline Review",
            "content": "Acme is worried about migration timeline and wants minimal disruption. They are also comparing us with Salesforce."
        }
    ]

    for exp in experiences:
        print(f"   - Retaining: {exp['deal_name']} ({exp['stage']})...")
        res = await hindsight_service.retain_interaction(
            deal_id=exp["deal_id"],
            deal_name=exp["deal_name"],
            company_name=exp["company"],
            deal_stage=exp["stage"],
            deal_value=exp["value"],
            deal_currency=exp["currency"],
            interaction_id=exp["inter_id"],
            interaction_type=exp["type"],
            interaction_title=exp["title"],
            interaction_content=exp["content"]
        )
        print(f"     Status: {res.status}")

    # 3. Perform Real Hindsight RECALL
    print("\n3. Executing REAL RECALL query...")
    query = "Find historical deals where customers were concerned about migration time or disruption. What approaches led to positive or negative outcomes?"
    print(f"   Query: '{query}'")

    recall_response = await hindsight_service.recall_memories(query=query, top_k=10)
    print(f"\n   Recall Status: {recall_response.get('status')}")
    print(f"   Total Recalled Count: {recall_response.get('count', 0)}")

    results = recall_response.get("results", [])
    print("\n   Recalled Evidence:")
    for idx, r in enumerate(results, 1):
        content = r.get("content", "")
        context = r.get("context", "N/A")
        print(f"   [{idx}] {content[:150]}...")
        print(f"       Context: {context}")

    if recall_response.get("status") == "success":
        print("\n" + "=" * 70)
        print(" REAL HINDSIGHT CLOUD RECALL VERIFICATION SUCCESSFUL ")
        print("=" * 70)
        return True
    else:
        print("   [FAIL] Recall response did not return status 'success'")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_phase3_real_recall_test())
    sys.exit(0 if success else 1)
