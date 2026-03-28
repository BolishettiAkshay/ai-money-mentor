from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.orchestrator_instance import orchestrator

router = APIRouter()

class QueryInput(BaseModel):
    message: str

@router.post("/analyze")
async def analyze_query(input_data: QueryInput):
    try:
        result = await orchestrator.analyze_query(input_data.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear")
async def clear_data():
    orchestrator.clear_history()
    return {"status": "History cleared"}
