from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.deal import Deal
from app.models.interaction import Interaction
from app.schemas.intelligence import DealRecallResponse, EvidenceItem, RecallRequestPayload
from app.services.hindsight import hindsight_service


class DealRecallService:
    def build_deal_intelligence_query(self, deal: Deal, custom_query: Optional[str] = None) -> str:
        if custom_query and custom_query.strip():
            return custom_query.strip()

        company_name = deal.company.name if deal.company else "Unknown Company"
        industry = deal.company.industry if deal.company and deal.company.industry else "Unspecified Industry"
        stage_str = deal.stage.value if hasattr(deal.stage, "value") else str(deal.stage)

        # Summarize key themes from recent interactions
        recent_interactions = deal.interactions[:3] if deal.interactions else []
        interaction_summaries = []
        for inter in recent_interactions:
            interaction_summaries.append(f"[{inter.type}] {inter.title}: {inter.content}")

        interaction_context = " ".join(interaction_summaries) if interaction_summaries else deal.description or ""

        query = (
            f"Find historical sales experiences similar to deal '{deal.name}' (Company: '{company_name}', Industry: '{industry}', Stage: {stage_str}). "
            f"Context and customer concerns: {interaction_context}. "
            f"Look for customer objections, migration or timeline concerns, competitor comparisons, technical evaluation risks, and both WON and LOST deal outcomes."
        )
        return query

    def detect_outcome_hint(self, content: str, tags: List[str]) -> Optional[str]:
        text_upper = content.upper()
        tags_lower = [t.lower() for t in tags]

        if "CLOSED_WON" in text_upper or "WON" in text_upper or "won" in tags_lower or "stage:closed_won" in tags_lower:
            return "WON"
        elif "CLOSED_LOST" in text_upper or "LOST" in text_upper or "lost" in tags_lower or "stage:closed_lost" in tags_lower:
            return "LOST"
        return "UNKNOWN"

    async def execute_recall_for_deal(
        self,
        db: Session,
        deal_id: str,
        payload: Optional[RecallRequestPayload] = None
    ) -> DealRecallResponse:
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deal with ID '{deal_id}' not found."
            )

        custom_query = payload.query if payload else None
        limit = payload.limit if payload else 10

        constructed_query = self.build_deal_intelligence_query(deal, custom_query)

        recall_res = await hindsight_service.recall_memories(
            query=constructed_query,
            top_k=limit
        )

        status_str = recall_res.get("status", "error")
        raw_items = recall_res.get("results", [])
        evidence_list: List[EvidenceItem] = []

        for item in raw_items:
            content = item.get("content", "")
            tags = item.get("tags", [])
            outcome = self.detect_outcome_hint(content, tags)

            evidence_list.append(
                EvidenceItem(
                    memory_id=str(item.get("id", "")),
                    content=content,
                    context=item.get("context"),
                    type=item.get("type", "GENERAL_EXPERIENCE"),
                    metadata=item.get("metadata", {}),
                    tags=tags,
                    outcome_hint=outcome
                )
            )

        return DealRecallResponse(
            deal_id=deal_id,
            query=constructed_query,
            results=evidence_list,
            count=len(evidence_list),
            status=status_str,
            message=recall_res.get("message")
        )


deal_recall_service = DealRecallService()
