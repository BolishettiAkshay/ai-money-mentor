import json
import os
from fastapi import APIRouter, HTTPException, Depends, UploadedFile, File
from pydantic import BaseModel
from typing import Dict, List, Optional
from sqlmodel import Session, select
from app.models import get_session, User, FinancialData as DBFinancialData, UploadedFile as DBUploadedFile, ChatHistory

router = APIRouter()

# Default User ID for local single-user demo
DEFAULT_USER_ID = 1

class FinancialDataSchema(BaseModel):
    userId: Optional[int] = DEFAULT_USER_ID
    income: float
    expenses: float
    savings: float
    debts: float = 0.0
    categories: Dict[str, float]

class ChatRequest(BaseModel):
    message: str
    userId: Optional[int] = DEFAULT_USER_ID

@router.post("/financial-data")
async def save_financial_data(data: FinancialDataSchema, session: Session = Depends(get_session)):
    try:
        # 1. Handle User Creation or Fetching
        user_id = data.userId
        
        if user_id:
            user = session.get(User, user_id)
            if not user:
                # If userId provided but not in DB, create it
                user = User(id=user_id, email=f"user{user_id}@example.com")
                session.add(user)
                session.commit()
                session.refresh(user)
        else:
            # Create new user if no userId provided
            user = User(email="newuser@example.com")
            session.add(user)
            session.commit()
            session.refresh(user)
            user_id = user.id

        # 2. Save Financial Data to DB
        db_data = DBFinancialData(
            user_id=user_id,
            income=data.income,
            expenses=data.expenses,
            savings=data.savings,
            debts=data.debts,
            categories=data.categories
        )
        session.add(db_data)
        session.commit()
        session.refresh(db_data)
        
        return {
            "status": "success", 
            "userId": user_id,
            "data": db_data
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/financial-data/{user_id}")
async def get_financial_data(user_id: int, session: Session = Depends(get_session)):
    try:
        statement = select(DBFinancialData).where(DBFinancialData.user_id == user_id).order_by(DBFinancialData.created_at.desc())
        latest = session.exec(statement).first()
        if not latest:
            raise HTTPException(status_code=404, detail="Financial data not found")
        return latest
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai-advisor")
async def ai_advisor(request: ChatRequest, session: Session = Depends(get_session)):
    try:
        message = request.message
        user_id = request.userId or DEFAULT_USER_ID

        # Fetch latest financial data from DB
        statement = select(DBFinancialData).where(DBFinancialData.user_id == user_id).order_by(DBFinancialData.created_at.desc())
        financial_data = session.exec(statement).first()

        # Build context-aware prompt
        if financial_data:
            prompt = f"""
You are FinWise AI, a smart financial advisor.

User Financial Data:
Income: ₹{financial_data.income}
Expenses: ₹{financial_data.expenses}
Savings: ₹{financial_data.savings}
Debts: ₹{financial_data.debts}
Categories: {json.dumps(financial_data.categories)}

User Question:
{message}

Instructions:
- Analyze the user's current financial situation.
- Identify overspending if categories are provided.
- Give specific, practical, and actionable advice.
- DO NOT ask for missing data if it is already provided above.
"""
        else:
            prompt = f"User Question: {message}\n\nNote: User has not provided financial data yet. Politely ask them to fill the form for personalized advice."

        # Rule-based logic for demo
        response = ""
        msg = message.lower()

        if not financial_data:
            response = "I don't have your financial profile yet. Please fill out the form so I can give you personalized advice!"
        else:
            income = financial_data.income
            expenses = financial_data.expenses
            savings = financial_data.savings
            debts = financial_data.debts
            categories = financial_data.categories or {}

            if "hello" in msg or "hi" in msg:
                response = f"Hello! I see you have a monthly income of ₹{income} and you're saving about ₹{savings}. How can I help you optimize your finances today?"
            elif "debt" in msg or "owe" in msg:
                if debts > 0:
                    response = f"You mentioned having ₹{debts} in debt. I recommend using the 'Debt Avalanche' or 'Debt Snowball' method to pay it off efficiently, starting with your highest interest debt first."
                else:
                    response = "You currently have no recorded debt. That's a great position to be in! Focus on building your investment portfolio."
            elif "overspend" in msg or "where" in msg:
                overspent = [cat for cat, amt in categories.items() if amt > (income * 0.15)]
                if overspent:
                    response = f"Looking at your records, you're spending a significant portion on {', '.join([c.capitalize() for c in overspent])}. Try to cap these at 10-15% of your income to increase your ₹{savings} savings."
                else:
                    response = "Your category spending looks very balanced based on the data you provided. Well done!"
            else:
                response = f"Based on your ₹{income} income and ₹{expenses} expenses, your savings rate is { (savings/income*100) if income > 0 else 0 :.1f}%. I recommend aiming for at least 20% by reviewing your variable costs."

        # Save chat to history
        chat_entry = ChatHistory(
            user_id=user_id,
            message=message,
            response=response
        )
        session.add(chat_entry)
        session.commit()

        return {"response": response}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_finance(data: FinancialDataSchema, session: Session = Depends(get_session)):
    # Redirect to the new financial-data logic
    return await save_financial_data(data, session)

@router.post("/chat")
async def chat_with_ai(request: ChatRequest, session: Session = Depends(get_session)):
    # Redirect to the new ai-advisor logic
    return await ai_advisor(request, session)

@router.get("/user-data/{user_id}")
async def get_user_data(user_id: int, session: Session = Depends(get_session)):
    try:
        statement = select(DBFinancialData).where(DBFinancialData.user_id == user_id).order_by(DBFinancialData.created_at.desc())
        latest = session.exec(statement).first()
        
        if not latest:
            raise HTTPException(status_code=404, detail="No data found for this user")

        return {
            "summary": {
                "income": latest.income,
                "expenses": latest.expenses,
                "savings": latest.savings,
                "debts": latest.debts,
                "savings_ratio": (latest.savings / latest.income * 100) if latest.income > 0 else 0
            },
            "categories": latest.categories,
            "created_at": latest.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
