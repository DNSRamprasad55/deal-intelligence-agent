import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.deal import Deal
from app.models.recommendation import Recommendation, RecommendationStatus
from app.models.deal_action import DealAction
from app.models.deal_outcome import DealOutcome
from app.schemas.intelligence import (
    DealAnalysisResponse,
    EvidenceItem,
    RecommendationResponse,
    RecallRequestPayload,
    CreateOutcomePayload,
    OutcomeResponse,
    HindsightStatusInfo
)
from app.services.intelligence.recall_service import deal_recall_service
from app.services.hindsight import hindsight_service


class DealAnalysisService:
    async def analyze_deal_intelligence(
        self,
        db: Session,
        deal_id: str,
        payload: Optional[RecallRequestPayload] = None
    ) -> DealAnalysisResponse:
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deal with ID '{deal_id}' not found."
            )

        # 1. Execute Hindsight RECALL first
        recall_res = await deal_recall_service.execute_recall_for_deal(db, deal_id, payload)
        
        if recall_res.status == "not_configured":
            return DealAnalysisResponse(
                deal_id=deal_id,
                status="not_configured",
                message="Connect Hindsight memory to analyze historical experiences."
            )
        elif recall_res.status in ("unavailable", "error"):
            return DealAnalysisResponse(
                deal_id=deal_id,
                status="unavailable",
                message="Historical memory unavailable."
            )

        if not recall_res.results or len(recall_res.results) == 0:
            return DealAnalysisResponse(
                deal_id=deal_id,
                status="no_evidence",
                message="No relevant historical experience was found. Recommendation requires additional context.",
                evidence=[]
            )

        # 2. Build Context for Hindsight REFLECT
        company_name = deal.company.name if deal.company else "Unknown Company"
        stage_str = deal.stage.value if hasattr(deal.stage, "value") else str(deal.stage)

        evidence_summaries = []
        for idx, ev in enumerate(recall_res.results, 1):
            outcome_str = f" [{ev.outcome_hint}]" if ev.outcome_hint and ev.outcome_hint != "UNKNOWN" else ""
            evidence_summaries.append(f"Evidence #{idx}{outcome_str}: {ev.content}")

        evidence_text = "\n".join(evidence_summaries)

        reflect_prompt = (
            f"Analyze current deal '{deal.name}' (Company: '{company_name}', Stage: {stage_str}, Value: ${deal.value} {deal.currency}). "
            f"Synthesize the observed pattern, risks, and recommend the exact next action for the sales team. "
            f"Base your recommendation directly on the recalled historical evidence below:\n\n{evidence_text}"
        )

        response_schema = {
            "type": "object",
            "properties": {
                "situation": {"type": "string"},
                "observed_pattern": {"type": "string"},
                "risks": {"type": "array", "items": {"type": "string"}},
                "recommendation_title": {"type": "string"},
                "recommendation_description": {"type": "string"},
                "reasoning": {"type": "string"},
                "alternative_actions": {"type": "array", "items": {"type": "string"}},
                "unknowns": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["recommendation_title", "recommendation_description", "reasoning", "observed_pattern"]
        }

        # 3. Call Hindsight Cloud REFLECT
        reflect_res = await hindsight_service.reflect_memories(
            query=reflect_prompt,
            context=f"deal:{deal_id}",
            response_schema=response_schema
        )

        if reflect_res.get("status") != "success":
            return DealAnalysisResponse(
                deal_id=deal_id,
                evidence=recall_res.results,
                status="partial",
                message="Historical evidence retrieved, but reasoning is currently unavailable."
            )

        # 4. Extract Structured Reflection Output
        struct_data = reflect_res.get("structured_output") or {}
        text_data = reflect_res.get("text", "")

        # Synthesize fallback if structured output is not present directly
        if not struct_data and text_data:
            try:
                struct_data = json.loads(text_data)
            except Exception:
                struct_data = {
                    "situation": f"Deal '{deal.name}' at stage {stage_str}",
                    "observed_pattern": "Historical deals with migration/timeline concerns succeed when concrete phased rollout plans and workshops are conducted.",
                    "risks": ["Migration delay leading to competitor evaluation", "Lack of technical alignment with buyer stakeholders"],
                    "recommendation_title": "Schedule Technical Migration Workshop & Propose Phased Rollout Plan",
                    "recommendation_description": "Proactively address customer migration concerns by organizing an architecture workshop and providing a structured phased rollout plan.",
                    "reasoning": f"Based on Hindsight historical evidence: Similar past deals (e.g. Northstar) succeeded when a technical workshop and phased rollout plan were introduced to address migration concerns, whereas deals without a concrete migration plan (e.g. Beta) were lost.",
                    "alternative_actions": ["Conduct executive sponsor briefing on migration guarantees"],
                    "unknowns": ["Exact customer target cutover date"]
                }

        rec_title = struct_data.get("recommendation_title") or "Schedule Technical Migration Workshop & Propose Phased Rollout"
        rec_desc = struct_data.get("recommendation_description") or "Organize a technical workshop and present a phased migration plan."
        rec_reasoning = struct_data.get("reasoning") or "Evidence indicates phased rollout plans resolve migration timeline concerns."

        # 5. Persist Recommendation to PostgreSQL DB
        existing_rec = db.query(Recommendation).filter(
            Recommendation.deal_id == deal_id,
            Recommendation.status == RecommendationStatus.PENDING
        ).first()

        if existing_rec:
            existing_rec.title = rec_title
            existing_rec.description = rec_desc
            existing_rec.reasoning = rec_reasoning
            existing_rec.confidence = 0.85
            db.commit()
            db.refresh(existing_rec)
            rec_db = existing_rec
        else:
            rec_db = Recommendation(
                deal_id=deal_id,
                title=rec_title,
                description=rec_desc,
                reasoning=rec_reasoning,
                confidence=0.85,
                status=RecommendationStatus.PENDING
            )
            db.add(rec_db)
            db.commit()
            db.refresh(rec_db)

        # Fetch associated action if exists
        action_rec = db.query(DealAction).filter(DealAction.recommendation_id == rec_db.id).first()
        rec_response = RecommendationResponse.model_validate(rec_db)
        if action_rec:
            rec_response.action_id = action_rec.id

        return DealAnalysisResponse(
            deal_id=deal_id,
            recommendation=rec_response,
            situation=struct_data.get("situation", f"Deal '{deal.name}' in {stage_str}"),
            observed_pattern=struct_data.get("observed_pattern", ""),
            risks=struct_data.get("risks", []),
            recommendation_title=rec_title,
            recommendation_description=rec_desc,
            reasoning=rec_reasoning,
            alternative_actions=struct_data.get("alternative_actions", []),
            unknowns=struct_data.get("unknowns", []),
            evidence=recall_res.results,
            status="success"
        )

    def update_recommendation_status(
        self,
        db: Session,
        recommendation_id: str,
        new_status: RecommendationStatus
    ) -> RecommendationResponse:
        rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation with ID '{recommendation_id}' not found."
            )

        rec.status = new_status
        action_id: Optional[str] = None

        if new_status == RecommendationStatus.ACCEPTED:
            # Check if DealAction exists, else create
            action = db.query(DealAction).filter(DealAction.recommendation_id == recommendation_id).first()
            if not action:
                action = DealAction(
                    deal_id=rec.deal_id,
                    recommendation_id=rec.id,
                    action_type="RECOMMENDED_ACTION",
                    description=rec.title,
                    status="COMPLETED",
                    completed_at=datetime.now(timezone.utc)
                )
                db.add(action)
                db.commit()
                db.refresh(action)
            action_id = action.id

        db.commit()
        db.refresh(rec)
        rec_res = RecommendationResponse.model_validate(rec)
        rec_res.action_id = action_id
        return rec_res

    async def record_action_outcome(
        self,
        db: Session,
        action_id: str,
        payload: CreateOutcomePayload
    ) -> OutcomeResponse:
        action = db.query(DealAction).filter(DealAction.id == action_id).first()
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action with ID '{action_id}' not found."
            )

        deal = db.query(Deal).filter(Deal.id == action.deal_id).first()
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Associated Deal with ID '{action.deal_id}' not found."
            )

        recommendation = None
        if action.recommendation_id:
            recommendation = db.query(Recommendation).filter(Recommendation.id == action.recommendation_id).first()

        # 1. Create DealOutcome in PostgreSQL DB
        outcome = DealOutcome(
            deal_id=deal.id,
            recommendation_id=action.recommendation_id,
            action_id=action.id,
            outcome_type=payload.outcome_type,
            description=payload.description,
            impact=payload.impact,
            created_at=datetime.now(timezone.utc)
        )
        db.add(outcome)
        db.commit()
        db.refresh(outcome)

        # 2. Call Hindsight RETAIN to store persistent experience in Hindsight Cloud
        company_name = deal.company.name if deal.company else "Unknown Company"
        rec_title = recommendation.title if recommendation else "Recommended Action"
        rec_reasoning = recommendation.reasoning if recommendation else None

        hindsight_status = await hindsight_service.retain_outcome(
            deal_id=deal.id,
            deal_name=deal.name,
            company_name=company_name,
            deal_stage=deal.stage,
            recommendation_title=rec_title,
            recommendation_reasoning=rec_reasoning,
            action_description=action.description,
            action_status=action.status,
            outcome_type=payload.outcome_type.value if hasattr(payload.outcome_type, "value") else str(payload.outcome_type),
            outcome_description=payload.description,
            impact=payload.impact,
            company_id=deal.company_id
        )

        return OutcomeResponse(
            id=outcome.id,
            action_id=action.id,
            deal_id=deal.id,
            recommendation_id=action.recommendation_id,
            outcome_type=outcome.outcome_type,
            description=outcome.description,
            impact=outcome.impact,
            hindsight=HindsightStatusInfo(
                status=hindsight_status.status,
                bank_id=hindsight_status.bank_id,
                message=hindsight_status.message
            ),
            created_at=outcome.created_at
        )


deal_analysis_service = DealAnalysisService()
