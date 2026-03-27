from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

class UserFinanceBase(BaseModel):
    income: int
    expenses: int
    savings: int
    investments: int
    goal: str

class UserFinanceCreate(UserFinanceBase):
    pass

class UserFinanceResponse(UserFinanceBase):
    id: int
    score: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChatInput(BaseModel):
    message: str
    user_data: Optional[Dict] = None

class AnalysisResponse(BaseModel):
    score: int
    plan: Dict[str, str]
    advice: str
    goal: Dict[str, str]
