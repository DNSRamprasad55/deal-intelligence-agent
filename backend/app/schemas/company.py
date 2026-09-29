from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.contact import ContactResponse


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = None
    size: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


class CompanyResponse(BaseModel):
    id: str
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    contacts: List[ContactResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
