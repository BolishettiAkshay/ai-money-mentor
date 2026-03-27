from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime
from typing import List

import models, schemas, database
from database import engine, get_db

# Create tables (In production, use migrations like Alembic)
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database error: {e}")

app = FastAPI(title="AI Money Mentor API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post("/analyze", response_model=schemas.AnalysisResponse)
def analyze_finance(data: schemas.UserFinanceCreate, db: Session = Depends(get_db)):
    # 1. Calculation logic
    income = data.income if data.income > 0 else 1
    savings_rate = data.savings / income
    
    if savings_rate >= 0.3:
        score = 85
    elif savings_rate >= 0.2:
        score = 70
    elif savings_rate >= 0.1:
        score = 55
    else:
        score = 40
        
    plan = {
        "save": f"₹{int(data.income * 0.2):,}",
        "invest": f"₹{int(data.income * 0.15):,}",
        "emergency": f"₹{int(data.income * 0.1):,}"
    }
    
    advice = "Your financial health is good, but you could optimize your non-essential spending."
    if score < 60:
        advice = "Focus on reducing high-interest debt and increasing your savings rate."
    elif score > 80:
        advice = "Excellent! Consider diversifying into more advanced investment vehicles."
        
    # 2. Store in DB
    new_record = models.UserFinance(
        income=data.income,
        expenses=data.expenses,
        savings=data.savings,
        investments=data.investments,
        goal=data.goal,
        score=score
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    return {
        "score": score,
        "plan": plan,
        "advice": advice,
        "goal": {
            "type": data.goal,
            "target": "₹5,00,000", # Placeholder logic
            "monthly": "₹15,000",
            "timeline": "36 Months"
        }
    }

@app.get("/dashboard-data")
def get_dashboard_data(db: Session = Depends(get_db)):
    # Return latest user record
    record = db.query(models.UserFinance).order_by(models.UserFinance.created_at.desc()).first()
    if not record:
        return {
            "income": 0,
            "expenses": 0,
            "savings": 0,
            "investments": 0,
            "score": 0
        }
    return record

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Basic analysis simulation
    return {
        "filename": file.filename,
        "total_transactions": 42, # Simulated
        "estimated_spending": "₹12,450" # Simulated
    }

@app.post("/chat")
def ai_chat(chat_input: schemas.ChatInput):
    msg = chat_input.message.lower()
    user_data = chat_input.user_data or {}
    income = user_data.get("income", 0)
    
    reply = "I'm your AI Money Mentor. How can I help you today?"
    
    if "save" in msg:
        reply = f"Based on your income of ₹{income}, I recommend saving at least 20%. Try setting up an auto-transfer to a high-yield savings account."
    elif "invest" in msg:
        reply = "Consider low-cost index funds or ELSS for tax savings. Always keep an emergency fund first."
    elif "expenses" in msg:
        reply = "Review your subscription services and dining out. Even small cuts can lead to large savings over time."
    elif "score" in msg:
        reply = "Your current money health score is calculated based on your savings-to-income ratio."
        
    return {"reply": reply}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
