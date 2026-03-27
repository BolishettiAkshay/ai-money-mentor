from sqlalchemy import Column, Integer, String, DateTime, Float
from database import Base
from datetime import datetime

class UserFinance(Base):
    __tablename__ = "users_finance"

    id = Column(Integer, primary_key=True, index=True)
    income = Column(Integer)
    expenses = Column(Integer)
    savings = Column(Integer)
    investments = Column(Integer)
    goal = Column(String(255))
    score = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
