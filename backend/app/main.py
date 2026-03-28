from fastapi import FastAPI
from app.agents.budget_agent import BudgetAgent

app = FastAPI()

budget_agent = BudgetAgent()

@app.get("/")
def root():
    return {"message": "System Running"}

@app.post("/test-budget")
def test_budget():
    data = {
        "savings": 50000,
        "expense": 80000
    }

    result = budget_agent.run(data)
    return result