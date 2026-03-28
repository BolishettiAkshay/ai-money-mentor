from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
import uuid
from services.orchestrator_instance import orchestrator

router = APIRouter()
UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Generate unique filename to avoid collisions
    file_id = str(uuid.uuid4())[:8]
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the file (extract text, chunk, embed, store)
        result = await orchestrator.process_file(file_path)
        
        return {
            "filename": file.filename,
            "status": "processed",
            "chunks": result["chunks_processed"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
