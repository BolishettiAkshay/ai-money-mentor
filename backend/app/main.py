import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import router from the app.routes
from app.routes.analyze import router as analyze_router

app = FastAPI(title="FinWise AI Local Backend")

# Enable CORS (Important for frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(analyze_router)

@app.get("/")
async def root():
    return {"status": "FinWise AI Backend is running locally"}

@app.get("/data")
async def get_data():
    try:
        if os.path.exists("data.json"):
            with open("data.json", "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
