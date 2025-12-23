from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
import asyncio
import json
from pydantic import BaseModel
from typing import List

router = APIRouter()

class MessagePart(BaseModel):
    type: str # 'text'
    content: str

class Message(BaseModel):
    role: str
    content: str | List[MessagePart]

class ChatRequest(BaseModel):
    messages: List[Message]

async def fake_stream_generator():
    # Simulate thinking
    yield "event: start\ndata: \n\n" 
    
    chunks = [
        "Hello! ", "I ", "see ", "you ", "uploaded ", "a ", "document. ", 
        "I ", "am ", "currently ", "running ", "in ", "mock ", "mode, ", 
        "but ", "soon ", "I ", "will ", "use ", "Gemini ", "or ", "OpenAI ", 
        "to ", "analyze ", "your ", "files ", "for ", "real."
    ]
    
    for chunk in chunks:
        await asyncio.sleep(0.1)
        # Format as SSE
        # Sending just data with the text delta. 
        # The tanstack client often expects specific JSON but let's try raw string first which is common for simple SSE adapters
        # Actually tanstack ai client typically expects JSON chunks representing the delta
        # Let's try to send a JSON that looks like { "type": "text", "content": chunk } or just the chunk string?
        # Safe bet: simple text delta if using 'text' event or default message
        yield f"data: {json.dumps(chunk)}\n\n"
    
    yield "event: end\ndata: \n\n"

from services.extraction import extractor
from database import get_db, File as FileModel
from services.agent import agent
from sqlalchemy.orm import Session
from fastapi import Depends
import re
import os

# ... imports ...



# ... imports ...

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    # ... (Prompt construction logic remains same) ...
    
    # Flatten last message content
    last_msg = request.messages[-1]
    last_content = ""
    if isinstance(last_msg.content, str):
        last_content = last_msg.content
    else:
        last_content = "\n".join([p.content for p in last_msg.content if p.type == 'text'])

    # Regex to find [FILE_ID: ...]
    file_matches = re.findall(r"\[FILE_ID: ([a-f0-9\-]+) FILENAME: .+?\]", last_content)
    
    context_text = ""
    for file_id in file_matches:
        db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
        if db_file and os.path.exists(db_file.file_path):
            extracted = extractor.extract_text(db_file.file_path)
            context_text += f"\n--- Content of {db_file.filename} ---\n{extracted}\n-------------------\n"
    
    if context_text:
        full_prompt = f"Context from uploaded files:\n{context_text}\n\nUser Query: {last_content}"
    else:
        full_prompt = last_content

    async def stream_generator():
        # Using PydanticAI streaming
        # Note: We need to handle the agent run inside the async generator
        
        # We might need to ensure the OPENAI_API_KEY is present or catch errors
        try:
            async with agent.run_stream(full_prompt) as result:
                yield "event: start\ndata: \n\n"
                async for chunk in result.stream():
                    # PydanticAI streams string chunks (usually)
                    yield f"data: {json.dumps(chunk)}\n\n"
                
            yield "event: end\ndata: \n\n"
            
        except Exception as e:
            # Fallback / Error handling
            print(f"AI Error: {e}")
            yield f"data: {json.dumps(f'Error generating response: {str(e)}. Please check your API key.')}\n\n"
            yield "event: end\ndata: \n\n"
    
    return StreamingResponse(stream_generator(), media_type="text/event-stream")
