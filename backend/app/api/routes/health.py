from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.core.config import settings
from app.schemas.health import HealthResponse
from app.services.hindsight import hindsight_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def check_health(db: Session = Depends(get_db)):
    # Test DB connection
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    # Test Hindsight status
    hs_status = await hindsight_service.get_status()

    return HealthResponse(
        status="ok",
        application="deal-intelligence-agent",
        environment=settings.APP_ENV,
        database=db_status,
        hindsight=hs_status.value.lower()
    )
