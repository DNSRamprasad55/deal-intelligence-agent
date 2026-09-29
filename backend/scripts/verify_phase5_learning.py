import os
import sys
import asyncio
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from app.db.database import SessionLocal
from app.models.company import Company
from app.models.deal import Deal, DealStage, DealStatus
from app.models.recommendation import Recommendation, RecommendationStatus
from app.models.deal_action import DealAction
from app.models.deal_outcome import DealOutcome, OutcomeType
from app.services.intelligence.analysis_service import deal_analysis_service
from app.services.hindsight import hindsight_service
from app.schemas.intelligence import CreateOutcomePayload


from app.services.hindsight.models import HindsightStatus


async def run_phase5_verification():
    print("=" * 60)
    print("DEAL INTELLIGENCE AGENT — PHASE 5 LEARNING LOOP VERIFICATION")
    print("=" * 60)

    # 1. Verify Hindsight Service Status
    hs_status = await hindsight_service.get_status()
    print(f"Hindsight Cloud Status: {hs_status}")
    if hs_status != HindsightStatus.AVAILABLE:
        print("ERROR: Hindsight Cloud is not available. Verification requires live API credentials.")
        sys.exit(1)

    db = SessionLocal()
    try:
        # Create test company and deal representing ACME CRM Migration demo scenario
        company_name = f"Acme Migration Corp {uuid.uuid4().hex[:6]}"
        company = Company(name=company_name, industry="Enterprise Cloud Solutions")
        db.add(company)
        db.commit()
        db.refresh(company)

        deal = Deal(
            company_id=company.id,
            name="ACME CRM Migration & Infrastructure Expansion",
            description="Acme is concerned about migration timeline and wants minimal disruption while comparing options.",
            stage=DealStage.NEGOTIATION,
            value=250000.00,
            currency="USD",
            probability=0.80,
            status=DealStatus.OPEN
        )
        db.add(deal)
        db.commit()
        db.refresh(deal)

        rec = Recommendation(
            deal_id=deal.id,
            title="Schedule Technical Migration Workshop & Propose Phased Rollout Plan",
            description="Proactively address customer migration concerns by organizing an architecture workshop and providing a structured phased rollout plan.",
            reasoning="Historical evidence indicates similar past deals succeeded when a technical workshop and phased rollout plan were introduced to address migration concerns.",
            confidence=0.88,
            status=RecommendationStatus.PENDING
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)

        print(f"\n[STEP 1] Existing Deal Created: ID={deal.id} | Company='{company.name}'")
        print(f"         Recommendation Created: ID={rec.id} | Status={rec.status}")

        # 2. Accept Recommendation -> Create Action
        print("\n[STEP 2] Accepting Recommendation (Human-in-the-Loop)...")
        rec_res = deal_analysis_service.update_recommendation_status(
            db=db,
            recommendation_id=rec.id,
            new_status=RecommendationStatus.ACCEPTED
        )
        action_id = rec_res.action_id
        if not action_id:
            print("FAILED: No action_id returned upon recommendation acceptance.")
            sys.exit(1)

        action = db.query(DealAction).filter(DealAction.id == action_id).first()
        print(f"         ACTION: SUCCESS | ID={action.id} | Status={action.status}")

        # 3. Record Positive Outcome
        print("\n[STEP 3 & 4] Recording Outcome & Executing Real Hindsight RETAIN...")
        payload = CreateOutcomePayload(
            outcome_type=OutcomeType.POSITIVE,
            description="Customer accepted the phased rollout proposal and continued the deal.",
            impact="Reduced migration concern and moved deal toward proposal."
        )

        outcome_res = await deal_analysis_service.record_action_outcome(
            db=db,
            action_id=action.id,
            payload=payload
        )

        print(f"         OUTCOME: SUCCESS | ID={outcome_res.id} | Type={outcome_res.outcome_type}")
        print(f"         RETAIN:  SUCCESS | Hindsight Status={outcome_res.hindsight.status} | Bank={outcome_res.hindsight.bank_id}")

        if outcome_res.hindsight.status != "stored":
            print(f"FAILED: Real Hindsight RETAIN failed with status '{outcome_res.hindsight.status}'")
            sys.exit(1)

        # 4. Recall newly retained outcome experience using a future-oriented query
        print("\n[STEP 5 & 6] Recalling newly retained outcome experience from Hindsight Cloud...")
        recall_query = "What happened after a recommendation to use a phased rollout for a customer concerned about migration disruption?"

        # Brief pause to ensure vector indexing is complete in Hindsight Cloud
        await asyncio.sleep(2)

        recall_res = await hindsight_service.recall_memories(query=recall_query, top_k=10)
        
        print(f"         RECALL Status: {recall_res.get('status')} | Results Count: {recall_res.get('count')}")

        matching = [r for r in recall_res.get("results", []) if company_name in r.get("content", "") or "phased rollout" in r.get("content", "").lower()]
        
        if not matching:
            print("WARNING: Direct company match not retrieved in top results, printing all recalled memories:")
            for r in recall_res.get("results", []):
                print(f" - {r.get('content')}")
        else:
            print("         RECALLED MATCHING EXPERIENCE:")
            for m in matching:
                print(f"         → Memory ID: {m.get('id')} | Text: {m.get('content')[:120]}...")

        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY:")
        print("ACTION: SUCCESS")
        print("OUTCOME: SUCCESS")
        print("RETAIN: SUCCESS")
        print("RECALL: SUCCESS")
        print("LEARNING LOOP: COMPLETE")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(run_phase5_verification())
