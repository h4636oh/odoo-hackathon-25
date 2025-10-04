from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

class RuleBase(BaseModel):
    request_id: str
    rule_description: str
    temp_manager: Optional[str] = None
    manager_required: bool = False
    approvers: List[str] = []
    compulsory_approvers: List[str] = []
    sequential: bool = False
    percentage_required: float = 50.0

class RuleCreate(RuleBase):
    pass

class RuleInDB(RuleBase):
    rule_id: str
    company_id: str
    created_at: datetime
    updated_at: datetime

class RuleResponse(RuleBase):
    rule_id: str
    created_at: datetime
