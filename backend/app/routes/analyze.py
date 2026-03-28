import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional

router = APIRouter()

DB_FILE = "data.json"

def save_data(entry):
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []
    except:
        data = []

    data.append(entry)

    with open(DB_FILE, "w") as f:
        json.dump(data, f)

class FinancialData(BaseModel):
    income: float
    expenses: float
    savings_goal: Optional[float] = 0
    categories: Optional[Dict[str, float]] = {
        "Food": 0,
        "Travel": 0,
        "Shopping": 0,
        "Entertainment": 0,
        "Others": 0
    }

class ChatInput(BaseModel):
    message: str
    previous_analysis: Optional[Dict] = None

def get_financial_advice(data: FinancialData):
    income = data.income
    expenses = data.expenses
    savings = income - expenses
    savings_ratio = (savings / income) * 100 if income > 0 else 0
    
    breakdown = data.categories or {}
    total_categorized = sum(breakdown.values())
    
    # User requested: Calculate total spending
    total_spent = expenses # Or sum of categories if preferred, but using provided 'expenses' as total
    
    if total_categorized < expenses:
        breakdown["Others"] = breakdown.get("Others", 0) + (expenses - total_categorized)

    insights = []
    
    # Rule 1: Food spending
    food_perc = (breakdown.get("Food", 0) / income) * 100 if income > 0 else 0
    if food_perc > 20:
        insights.append("🍔 You're spending over 20% of your income on food. Try meal prepping to save more.")
    elif food_perc > 10:
        insights.append("🥗 Food expenses are moderate, but there's room for optimization.")
    
    # Rule 2: Savings ratio
    if savings_ratio < 20:
        insights.append("📉 Your savings rate is below the recommended 20%. Consider cutting non-essential costs.")
    else:
        insights.append("✅ Great job! You're saving more than 20% of your income.")

    # Rule 3: Entertainment
    ent_perc = (breakdown.get("Entertainment", 0) / income) * 100 if income > 0 else 0
    if ent_perc > 15:
        insights.append("🎬 Entertainment costs are a bit high. Maybe review your subscriptions?")

    # User requested: Detect overspending and highlight high-spend categories
    max_cat = max(breakdown.items(), key=lambda x: x[1]) if breakdown else ("None", 0)
    if max_cat[1] > (income * 0.3):
        insights.append(f"⚠️ High spending detected in {max_cat[0]}. It accounts for { (max_cat[1]/income)*100 if income > 0 else 0:.1f}% of your income.")

    # Plan generation
    plan = {
        "savings": {
            "amount": max(0, savings * 0.5),
            "label": "High-Yield Savings",
            "description": "Keep this liquid for immediate needs."
        },
        "investment": {
            "amount": max(0, savings * 0.3),
            "label": "Index Funds / Stocks",
            "description": "Long-term wealth building."
        },
        "emergency": {
            "amount": max(0, savings * 0.2),
            "label": "Emergency Fund",
            "description": "Safety net for unexpected expenses."
        }
    }

    result = {
        "breakdown": {cat: {"amount": amt, "percentage": (amt/income)*100 if income > 0 else 0} for cat, amt in breakdown.items()},
        "insights": insights,
        "plan": plan,
        "summary": {
            "income": income,
            "expenses": expenses,
            "savings": savings,
            "savings_ratio": savings_ratio,
            "total_spent": total_spent,
            "savings_goal": data.savings_goal
        }
    }
    
    # Save user data
    save_data(result)
    
    return result

@router.post("/analyze")
async def analyze_finance(data: FinancialData):
    try:
        return get_financial_advice(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_with_ai(input_data: ChatInput):
    msg = input_data.message.lower()
    analysis = input_data.previous_analysis
    
    if not analysis:
        return {"response": "I need your financial data to help you. Please complete the analysis first!"}

    summary = analysis.get("summary", {})
    breakdown = analysis.get("breakdown", {})
    
    # Simple Keyword Matching
    if "overspend" in msg or "spent" in msg or "where" in msg:
        max_cat = max(breakdown.items(), key=lambda x: x[1]['amount'])
        return {"response": f"Based on your data, you're spending the most on **{max_cat[0]}** (₹{max_cat[1]['amount']:.2f}). This accounts for {max_cat[1]['percentage']:.1f}% of your income."}
    
    if "save" in msg or "how" in msg:
        if summary.get("savings_ratio", 0) < 20:
            return {"response": "To save more, I recommend the 50/30/20 rule: 50% for Needs, 30% for Wants, and 20% for Savings. Start by tracking small daily expenses."}
        else:
            return {"response": "You're already doing great! To level up, consider automating your investments or looking for ways to increase your primary income."}

    if "afford" in msg:
        savings = summary.get("savings", 0)
        return {"response": f"Your current monthly savings is ₹{savings:.2f}. If the item costs less than this, you can afford it without touching your reserves. However, I'd recommend keeping at least 3-6 months of expenses as an emergency fund first."}

    return {"response": "I'm your FinWise AI. I can help you understand your spending, find ways to save, or check if you can afford something. Ask me about your overspending or savings!"}
