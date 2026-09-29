from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.interaction import InteractionCreate, InteractionResponse
from app.services.interaction_service import interaction_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/deals/{deal_id}/interactions", tags=["interactions"])


@router.post("", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def create_interaction(
    deal_id: str,
    interaction_in: InteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await interaction_service.create_interaction(
        db=db,
        deal_id=deal_id,
        interaction_in=interaction_in,
        user_id=current_user.id
    )


@router.get("", response_model=List[InteractionResponse])
def list_interactions(
    deal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return interaction_service.list_interactions_for_deal(db, deal_id)
