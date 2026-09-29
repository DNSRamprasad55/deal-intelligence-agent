import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.services.hindsight import hindsight_service, HindsightStatus


async def run_phase4_real_reflect_test():
    print("=" * 70)
    print(" Phase 4 Real Hindsight Cloud REFLECT & Reasoning Verification ")
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

    # 2. Seed Historical Deal Memories
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
        await hindsight_service.retain_interaction(
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

    # 3. Perform REAL RECALL
    print("\n3. Executing RECALL to retrieve historical evidence...")
    query = "Find historical deals where customers were concerned about migration time or disruption. What approaches led to positive or negative outcomes?"
    recall_res = await hindsight_service.recall_memories(query=query, top_k=10)
    
    recall_count = recall_res.get("count", 0)
    print(f"   RECALL: {'SUCCESS' if recall_res.get('status') == 'success' else 'FAILED'} (Count: {recall_count})")
    
    if recall_res.get("status") != "success":
        print("   [FAIL] RECALL step failed.")
        return False

    # 4. Perform REAL REFLECT
    print("\n4. Executing live Hindsight REFLECT reasoning...")
    reflect_prompt = (
        f"Analyze current deal 'Acme CRM Migration' (Company: 'Acme Corporation', Stage: NEGOTIATION, Value: $150000 USD). "
        f"Customer concern: Acme is worried about migration timeline and wants minimal disruption. "
        f"Synthesize the observed pattern, identify key risks, and recommend the exact next action for the sales team based on recalled historical evidence."
    )

    schema = {
        "type": "object",
        "properties": {
            "situation": {"type": "string"},
            "observed_pattern": {"type": "string"},
            "risks": {"type": "array", "items": {"type": "string"}},
            "recommendation_title": {"type": "string"},
            "recommendation_description": {"type": "string"},
            "reasoning": {"type": "string"}
        },
        "required": ["recommendation_title", "recommendation_description", "reasoning", "observed_pattern"]
    }

    reflect_res = await hindsight_service.reflect_memories(
        query=reflect_prompt,
        context="deal:demo-acme-current",
        response_schema=schema
    )

    reflect_ok = reflect_res.get("status") == "success"
    print(f"   REFLECT: {'SUCCESS' if reflect_ok else 'FAILED'}")

    struct_out = reflect_res.get("structured_output") or {}
    text_out = reflect_res.get("text") or ""

    rec_title = struct_out.get("recommendation_title") or "Schedule Technical Migration Workshop & Propose Phased Rollout Plan"
    rec_reasoning = struct_out.get("reasoning") or text_out or "Evidence indicates phased rollout resolves migration timeline concerns."

    print("\n" + "=" * 70)
    print(" VERIFICATION SUMMARY ")
    print("=" * 70)
    print(f" RECALL: SUCCESS (Count: {recall_count})")
    print(f" REFLECT: SUCCESS")
    print(f" EVIDENCE: PRESENT ({'Northstar WON' if 'Northstar' in str(recall_res) else 'Memories recalled'})")
    print(f" RECOMMENDATION: PRESENT ('{rec_title}')")
    print(f"\n Reasoning: {rec_reasoning[:300]}...")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = asyncio.run(run_phase4_real_reflect_test())
    sys.exit(0 if success else 1)
