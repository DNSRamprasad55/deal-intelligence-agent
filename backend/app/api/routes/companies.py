from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.company import CompanyCreate, CompanyResponse
from app.schemas.contact import ContactCreate, ContactResponse
from app.services.company_service import company_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    company_in: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return company_service.create_company(db, company_in)


@router.get("", response_model=List[CompanyResponse])
def list_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return company_service.list_companies(db, skip=skip, limit=limit)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return company_service.get_company_by_id(db, company_id)


@router.post("/{company_id}/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def add_contact(
    company_id: str,
    contact_in: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return company_service.add_contact(db, company_id, contact_in)
