from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class RequestBase(BaseModel):
    requestor: str
    request_description: str
    expense_date: datetime
    category: str
    paidBy: str
    payment_Currency: str
    payment_Amount: float
    remarks: Optional[str] = None
    status: str = "submitted"

class RequestCreate(RequestBase):
    pass

class RequestUpdate(BaseModel):
    status: Optional[str] = None
    rule_description: Optional[str] = None

class RequestInDB(RequestBase):
    request_id: str
    company_id: str
    created_at: datetime
    updated_at: datetime
    rule_description: Optional[str] = None

class RequestResponse(RequestBase):
    request_id: str
    created_at: datetime
    updated_at: datetime
    rule_description: Optional[str] = None

class RequestDetailResponse(RequestInDB):
    pass
