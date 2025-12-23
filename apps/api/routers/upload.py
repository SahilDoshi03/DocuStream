from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from database import get_db, File as FileModel, Chat
import shutil
import os
import uuid
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    chat_id: str = Form(None), # Optional chat_id linkage
    db: Session = Depends(get_db)
):
    valid_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    safe_filename = f"{valid_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

    # Create DB entry
    db_file = FileModel(
        id=valid_id,
        chat_id=chat_id,
        filename=file.filename,
        file_path=file_path,
        file_size=0 # TODO: Get size
    )
    
    # If file attached to a new chat, we might handle chat creation elsewhere or client sends ID.
    # For now, just save it.
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "url": f"/uploads/{safe_filename}" # We'll need to serve static files
    }
