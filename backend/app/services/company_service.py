from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.company import Company
from app.models.contact import Contact
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.schemas.contact import ContactCreate


class CompanyService:
    def create_company(self, db: Session, company_in: CompanyCreate) -> Company:
        company = Company(
            name=company_in.name,
            industry=company_in.industry,
            size=company_in.size,
            website=company_in.website,
            description=company_in.description
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    def get_company_by_id(self, db: Session, company_id: str) -> Company:
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID '{company_id}' not found."
            )
        return company

    def list_companies(self, db: Session, skip: int = 0, limit: int = 100) -> List[Company]:
        return db.query(Company).order_by(Company.name.asc()).offset(skip).limit(limit).all()

    def add_contact(self, db: Session, company_id: str, contact_in: ContactCreate) -> Contact:
        self.get_company_by_id(db, company_id)
        contact = Contact(
            company_id=company_id,
            name=contact_in.name,
            job_title=contact_in.job_title,
            email=contact_in.email,
            role_in_deal=contact_in.role_in_deal
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact


company_service = CompanyService()
