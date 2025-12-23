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

from services.extraction import extractor
from services.chunker import chunk_text
from services.vector_store import vector_store

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
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    # RAG: Index the file immediately
    try:
        # 1. Extract Text
        full_text = extractor.extract_text(file_path)
        
        if full_text:
            # 2. Chunk Text
            chunks = chunk_text(full_text)
            
            # 3. Prepare Documents for Vector Store
            documents = []
            for chunk in chunks:
                documents.append({
                    "text": chunk,
                    "metadata": {
                        "file_id": valid_id,
                        "filename": file.filename
                    }
                })
            
            # 4. Index
            vector_store.add_documents(documents)
            print(f"Indexed {len(documents)} chunks for file {file.filename}")
            
    except Exception as e:
        print(f"Indexing failed for {file.filename}: {e}")
        # We don't fail the upload, just log the error
        # In a real app, maybe update a status flag on the file

    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "url": f"/uploads/{safe_filename}" 
    }
