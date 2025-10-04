from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str  # "admin", "manager", "employee"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    manager_id: Optional[str] = None

class UserInDB(UserBase):
    user_id: str
    password_hash: str
    refresh_token_hash: Optional[str] = None
    approved_requests: List[str] = []
    rejected_requests: List[str] = []
    pending_requests: List[str] = []
    manager_id: Optional[str] = None
    to_approve_requests: List[str] = []
    has_approved_requests: List[str] = []
    has_rejected_requests: List[str] = []
    created_at: datetime
    updated_at: datetime

class UserResponse(UserBase):
    user_id: str
    manager: Optional[dict] = None
    created_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None
