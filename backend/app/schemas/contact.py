from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    job_title: Optional[str] = None
    email: Optional[EmailStr] = None
    role_in_deal: Optional[str] = None


class ContactResponse(BaseModel):
    id: str
    company_id: str
    name: str
    job_title: Optional[str] = None
    email: Optional[str] = None
    role_in_deal: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
