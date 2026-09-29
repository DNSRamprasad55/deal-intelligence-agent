from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.interaction import Interaction
from app.models.deal import Deal
from app.models.contact import Contact
from app.schemas.interaction import InteractionCreate, HindsightStatusDetail
from app.services.hindsight import hindsight_service


class InteractionService:
    async def create_interaction(
        self,
        db: Session,
        deal_id: str,
        interaction_in: InteractionCreate,
        user_id: Optional[str] = None
    ) -> Interaction:
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deal with ID '{deal_id}' not found."
            )

        company_name = deal.company.name if deal.company else "Unknown Company"
        contact_name = None
        if interaction_in.contact_id:
            contact = db.query(Contact).filter(Contact.id == interaction_in.contact_id).first()
            if contact:
                contact_name = contact.name

        # 1. Save to PostgreSQL
        interaction = Interaction(
            deal_id=deal_id,
            contact_id=interaction_in.contact_id,
            type=interaction_in.type,
            title=interaction_in.title,
            content=interaction_in.content,
            occurred_at=interaction_in.occurred_at,
            created_by=user_id
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        # 2. Perform Hindsight Cloud RETAIN
        retain_res = await hindsight_service.retain_interaction(
            deal_id=deal.id,
            deal_name=deal.name,
            company_name=company_name,
            deal_stage=deal.stage,
            deal_value=deal.value,
            deal_currency=deal.currency,
            interaction_id=interaction.id,
            interaction_type=interaction.type,
            interaction_title=interaction.title,
            interaction_content=interaction.content,
            contact_name=contact_name
        )

        setattr(interaction, "hindsight_memory_status", retain_res.status)
        setattr(
            interaction,
            "hindsight",
            HindsightStatusDetail(
                status=retain_res.status,
                bank_id=retain_res.bank_id,
                message=retain_res.message
            )
        )

        return interaction

    def list_interactions_for_deal(self, db: Session, deal_id: str) -> List[Interaction]:
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deal with ID '{deal_id}' not found."
            )
        return db.query(Interaction).filter(Interaction.deal_id == deal_id).order_by(Interaction.occurred_at.desc()).all()


interaction_service = InteractionService()
