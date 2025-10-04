from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid

class CompanyBase(BaseModel):
    company_name: str
    country: str
    admin_email: EmailStr

class CompanyCreate(CompanyBase):
    admin_password: str

class CompanySignup(BaseModel):
    email: EmailStr
    password: str
    company_name: str
    country: str

class CompanyInDB(CompanyBase):
    company_id: str
    admin_password_hash: str
    created_at: datetime
    updated_at: datetime

class CompanyResponse(CompanyBase):
    company_id: str
    created_at: datetime
