from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.deal import DealCreate, DealUpdate, DealResponse, DashboardMetricsResponse
from app.services.deal_service import deal_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/deals", tags=["deals"])


@router.post("", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
def create_deal(
    deal_in: DealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return deal_service.create_deal(db, deal_in, owner_id=current_user.id)


@router.get("/dashboard", response_model=DashboardMetricsResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return deal_service.get_dashboard_metrics(db)


@router.get("", response_model=List[DealResponse])
def list_deals(
    skip: int = 0,
    limit: int = 100,
    stage: Optional[str] = Query(None),
    status_val: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return deal_service.list_deals(db, skip=skip, limit=limit, stage=stage, status_val=status_val)


@router.get("/{deal_id}", response_model=DealResponse)
def get_deal(
    deal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return deal_service.get_deal_by_id(db, deal_id)


@router.put("/{deal_id}", response_model=DealResponse)
def update_deal(
    deal_id: str,
    deal_in: DealUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return deal_service.update_deal(db, deal_id, deal_in)
