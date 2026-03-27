from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime
from typing import List, Dict

import models, schemas, database
from database import engine, get_db

# Create tables
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database error: {e}")

app = FastAPI(title="AI Money Mentor API")

# Enable CORS (MANDATORY)
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

@app.get("/")
async def root():
    return {"status": "Backend is running"}

@app.post("/analyze", response_model=schemas.AnalysisResponse)
async def analyze_finance(data: schemas.UserFinanceCreate, db: Session = Depends(get_db)):
    print("Incoming data:", data.dict())
    try:
        income = data.income
        expenses = data.expenses
        savings = data.savings
        investments = data.investments
        goal = data.goal

        if income <= 0:
            raise HTTPException(status_code=400, detail="Income must be greater than 0")

        savings_rate = savings / income
        
        if savings_rate >= 0.3:
            score = 85
        elif savings_rate >= 0.2:
            score = 70
        elif savings_rate >= 0.1:
            score = 55
        else:
            score = 40
            
        plan = {
            "save": f"{int(income * 0.2)}",
            "invest": f"{int(income * 0.15)}",
            "emergency": f"{int(income * 0.1)}"
        }
        
        advice = "Reduce unnecessary expenses and increase savings."
        if score < 60:
            advice = "Focus on reducing high-interest debt and increasing your savings rate."
        elif score > 80:
            advice = "Excellent! Consider diversifying into more advanced investment vehicles."
            
        # Store in DB
        new_record = models.UserFinance(
            income=income,
            expenses=expenses,
            savings=savings,
            investments=investments,
            goal=goal,
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
                "type": goal,
                "target": "₹5,00,000",
                "monthly": "₹15,000",
                "timeline": "36 Months"
            }
        }
    except Exception as e:
        print(f"Error in /analyze: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard-data")
async def get_dashboard_data(db: Session = Depends(get_db)):
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
    return {
        "filename": file.filename,
        "total_transactions": 42,
        "estimated_spending": "₹12,450"
    }

@app.post("/chat")
async def ai_chat(chat_input: schemas.ChatInput):
    msg = chat_input.message.lower()
    user_data = chat_input.user_data or {}
    income = user_data.get("income", 0)
    expenses = user_data.get("expenses", 0)
    
    reply = "I'm your AI Money Mentor. How can I help you today?"
    
    if "save" in msg:
        reply = f"You should save at least ₹{int(float(income) * 0.2)} monthly."
    elif "invest" in msg:
        reply = "Consider low-cost index funds or ELSS for tax savings. Always keep an emergency fund first."
    elif "expenses" in msg:
        if float(expenses) > float(income) * 0.7:
            reply = "Your expenses are too high. Try reducing discretionary spending."
        else:
            reply = "Your expenses are under control."
    elif "score" in msg:
        reply = "Your current money health score is calculated based on your savings-to-income ratio."
        
    return {"reply": reply}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
