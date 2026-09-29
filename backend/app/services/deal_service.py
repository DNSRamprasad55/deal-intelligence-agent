from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.deal import Deal, DealStatus, DealStage
from app.models.interaction import Interaction
from app.schemas.deal import DealCreate, DealUpdate, DashboardMetricsResponse


class DealService:
    def create_deal(self, db: Session, deal_in: DealCreate, owner_id: Optional[str] = None) -> Deal:
        deal = Deal(
            company_id=deal_in.company_id,
            owner_id=owner_id,
            name=deal_in.name,
            description=deal_in.description,
            stage=deal_in.stage,
            value=deal_in.value,
            currency=deal_in.currency,
            probability=deal_in.probability,
            expected_close_date=deal_in.expected_close_date,
            status=deal_in.status
        )
        db.add(deal)
        db.commit()
        db.refresh(deal)
        return deal

    def get_deal_by_id(self, db: Session, deal_id: str) -> Deal:
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deal with ID '{deal_id}' not found."
            )
        return deal

    def update_deal(self, db: Session, deal_id: str, deal_in: DealUpdate) -> Deal:
        deal = self.get_deal_by_id(db, deal_id)
        update_data = deal_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(deal, field, value)
            
        # Automatically align deal status if stage changes
        if "stage" in update_data:
            if deal.stage == DealStage.CLOSED_WON:
                deal.status = DealStatus.WON
            elif deal.stage == DealStage.CLOSED_LOST:
                deal.status = DealStatus.LOST
            elif deal.status != DealStatus.OPEN and deal.stage not in (DealStage.CLOSED_WON, DealStage.CLOSED_LOST):
                deal.status = DealStatus.OPEN

        db.commit()
        db.refresh(deal)
        return deal

    def list_deals(self, db: Session, skip: int = 0, limit: int = 100, stage: Optional[str] = None, status_val: Optional[str] = None) -> List[Deal]:
        query = db.query(Deal)
        if stage:
            query = query.filter(Deal.stage == stage)
        if status_val:
            query = query.filter(Deal.status == status_val)
        return query.order_by(Deal.created_at.desc()).offset(skip).limit(limit).all()

    def get_dashboard_metrics(self, db: Session) -> DashboardMetricsResponse:
        total_active_deals = db.query(func.count(Deal.id)).filter(Deal.status == DealStatus.OPEN).scalar() or 0
        
        open_pipeline_val = db.query(func.sum(Deal.value)).filter(Deal.status == DealStatus.OPEN).scalar()
        open_pipeline_value = Decimal(str(open_pipeline_val)) if open_pipeline_val else Decimal("0.00")
        
        won_deals = db.query(func.count(Deal.id)).filter(Deal.status == DealStatus.WON).scalar() or 0
        lost_deals = db.query(func.count(Deal.id)).filter(Deal.status == DealStatus.LOST).scalar() or 0
        
        recent_deals = db.query(Deal).order_by(Deal.created_at.desc()).limit(5).all()
        recent_interactions = db.query(Interaction).order_by(Interaction.occurred_at.desc()).limit(5).all()
        
        return DashboardMetricsResponse(
            total_active_deals=total_active_deals,
            open_pipeline_value=open_pipeline_value,
            won_deals=won_deals,
            lost_deals=lost_deals,
            recent_deals=recent_deals,
            recent_interactions=recent_interactions
        )


deal_service = DealService()
