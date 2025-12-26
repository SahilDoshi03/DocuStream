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
    content: str | List[MessagePart] | None = None


class ChatRequest(BaseModel):
    messages: List[Message]
    industry: str | None = None
    chat_id: str | None = None

# ... imports ...
from services.agent import agent, model
from typing import Union
from pydantic_ai import Agent

from database import get_db, File as FileModel, Chat as ChatModel, Message as MessageModel
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import Depends, HTTPException, Path
import uuid
import re
import os

from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, UserPromptPart
from services.vector_store import vector_store
from prompts.industries import INDUSTRY_PROMPTS

@router.get("/chats")
def list_chats(db: Session = Depends(get_db)):
    chats = db.query(ChatModel).order_by(desc(ChatModel.created_at)).all()
    return [{"id": c.id, "title": c.title, "created_at": c.created_at} for c in chats]

@router.get("/chats/{chat_id}")
def get_chat(chat_id: str, db: Session = Depends(get_db)):
    chat = db.query(ChatModel).filter(ChatModel.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # We need to map DB messages to the format expected by the frontend/pydantic-ai
    # Frontend expects: { id: str, role: str, parts: [...] }
    # DB has content as text (or potentially JSON string if we decide later).
    # Current DB model has content=Text.
    result_messages = []
    for msg in chat.messages: # relying on relationship back_populates="messages" -> order? default DB order might not be guaranteed.
        # Should probably order by created_at.
        pass
    
    # Re-query messages with order
    messages = db.query(MessageModel).filter(MessageModel.chat_id == chat_id).order_by(MessageModel.created_at).all()
    
    formatted = []
    for m in messages:
        formatted.append({
            "id": m.id,
            "role": m.role,
            "parts": [{"type": "text", "content": m.content}]
        })
    return formatted

@router.delete("/chats/{chat_id}")
def delete_chat(chat_id: str, db: Session = Depends(get_db)):
    chat = db.query(ChatModel).filter(ChatModel.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    db.delete(chat)
    db.commit()
    return {"status": "success", "id": chat_id}

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    # Persist Chat Session
    chat_id = request.chat_id
    if not chat_id:
        chat_id = str(uuid.uuid4())
    
    chat_session = db.query(ChatModel).filter(ChatModel.id == chat_id).first()
    if not chat_session:
        chat_session = ChatModel(id=chat_id, title="New Chat")
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
    
    # Save User Message
    last_msg_obj = request.messages[-1]
    last_content_str = ""
    if isinstance(last_msg_obj.content, str):
        last_content_str = last_msg_obj.content
    elif isinstance(last_msg_obj.content, list):
         last_content_str = "\n".join([p.content for p in last_msg_obj.content if p.type == 'text'])
    
    user_msg_id = str(uuid.uuid4())
    user_message = MessageModel(
        id=user_msg_id,
        chat_id=chat_id,
        role="user",
        content=last_content_str
    )
    db.add(user_message)
    db.commit()

    # ... (Prompt construction logic remains same) ...
    # We need to preserve the setup code (retrieval, history building)
    
    # Flatten last message content
    last_msg = request.messages[-1]
    last_content = ""
    if isinstance(last_msg.content, str):
        last_content = last_msg.content
    elif last_msg.content is None:
        last_content = ""
    else:
        last_content = "\n".join([p.content for p in last_msg.content if p.type == 'text'])

    # RAG Retrieval
    # We search the vector store for chunks relevant to the latest user query
    context_chunks = vector_store.search(last_content, k=5)
    
    context_text = ""
    if context_chunks:
        context_text = "Relevant context from knowledge base:\n"
        for i, chunk in enumerate(context_chunks):
            # Include filename if available in metadata
            source = chunk.get("filename", "Unknown File")
            context_text += f"\n--- Chunk {i+1} from {source} (Score: {chunk.get('score', 0):.2f}) ---\n{chunk['text']}\n"
    
    if context_text:
        full_prompt = f"{context_text}\n\nUser Query: {last_content}"
        print(f"RAG: Injected {len(context_chunks)} chunks into context.")
    else:
        full_prompt = last_content

    # Build Message History
    message_history = []
    # Iterate over all messages except the last one (which is the new prompt)
    for msg in request.messages[:-1]:
        content_str = ""
        if isinstance(msg.content, str):
             content_str = msg.content
        elif isinstance(msg.content, list):
             content_str = "\n".join([p.content for p in msg.content if p.type == 'text'])
        
        if not content_str: 
             continue

        if msg.role == 'user':
            message_history.append(ModelRequest(parts=[UserPromptPart(content=content_str)]))
        elif msg.role == 'assistant':
            message_history.append(ModelResponse(parts=[TextPart(content=content_str)]))

    # Dynamic Agent Configuration
    active_agent = agent
    
    print(f"DEBUG INCOMING REQUEST: Industry='{request.industry}'")
    if request.industry:
        industry_prompt = INDUSTRY_PROMPTS.get(request.industry)
        if industry_prompt and model:
            try:
                # Base system prompt with industry context
                # We append instructions about "Conversational vs Extraction" behavior
                system_prompt = (
                    f"{industry_prompt}\n\n"
                    "IMPORTANT: You are in Hybrid Mode. "
                    "If the user asks a conversational question, reply with text. "
                    "If the user asks to extract data, analyze the document, or get the summary, return valid JSON matching the schema."
                )

                if request.industry == "banking":
                    from schemas.banking import BankingExtraction
                    # Schema-enforced Mode
                    # We use a minimal system prompt that forces tool usage and relies on the Pydantic model for schema definition.
                    # We avoid feeding the text-based schema from INDUSTRY_PROMPTS as it confuses the model.
                    refined_system_prompt = (
                         "You are a strict data extraction engine. You are forbidden from speaking.\n"
                         "You must ONLY call the `BankingExtraction` tool with data from the document.\n"
                         "If you cannot extract data, call the tool with null values.\n"
                         "Outputting text or markdown is a system violation."
                    )
                    active_agent = Agent(model, result_type=BankingExtraction, system_prompt=refined_system_prompt)
                    print(f"Switched to Extraction Agent (Schema: {request.industry})")
                else:
                    # Prompt-only Mode (for now, until other schemas are defined)
                    # For other industries, we just inject the prompt. 
                    active_agent = Agent(model, system_prompt=industry_prompt)
                    print(f"Switched to Extraction Agent (Prompt: {request.industry})")
            
            except Exception as e:
                print(f"Failed to configure agent: {e}")

    async def stream_generator():
        yield "event: start\ndata: \n\n"
        accumulated_response = ""
        
        try:
             # Send custom chunk with chat_id so client knows it
            chat_id_chunk = {
                "type": "chat_id", # Client needs to handle this or ignore it
                "chatId": chat_id
            }
            # We don't want to break standard parsers, so maybe sending it in a specific way?
            # Standard AI SDK might ignore unknown types. 
            # Or we just don't expect client to read it from stream, but we save it backend side correctly.
            # Client (if implementing logic) can read it.
            # yield f"data: {json.dumps(chat_id_chunk)}\n\n" 

            # Determine if we are in STRICT Extraction Mode (Banking)
            is_strict_extraction = request.industry == "banking"

            if is_strict_extraction:
                # ... (Existing strict extraction logic) ... 
                # (We need to capture the output to accumulated_response)
                
                # ... [Copying strict logic and adding accumulation] ...
                 # Instructor Pattern: LLM -> Pydantic Model
                # We implement a retry loop to force the model to use the tool if it refuses (returns text).
                print("Executing Strict Extraction...")
                
                max_retries = 2
                attempt = 0
                extraction_model = None
                
                # First attempt
                result = await active_agent.run(full_prompt, message_history=message_history)
                
                while attempt < max_retries:
                    result_data = result.output # 'output' is the attribute for result data
                    
                    if not isinstance(result_data, str):
                        # Success: We got a Pydantic model
                        extraction_model = result_data
                        break
                    
                    # Failure: Model returned text. Retry.
                    print(f"Extraction Failed (Attempt {attempt+1}/{max_retries}): Model output text: {result_data[:50]}...")
                    attempt += 1
                    
                    # Feed the refusal back to the model
                    retry_prompt = "Server Error: You replied with text. You MUST call the `BankingExtraction` tool to return data. Do not speak."
                    result = await active_agent.run(retry_prompt, message_history=result.new_messages())
                
                # Final check
                if extraction_model:
                     json_str = extraction_model.model_dump_json(indent=2)
                else:
                    # Final fallback if retries failed
                    result_data = result.output
                    if isinstance(result_data, str):
                         try:
                            clean_json = result_data.replace("```json", "").replace("```", "").strip()
                            json.loads(clean_json)
                            json_str = clean_json
                         except:
                            json_str = json.dumps({"error": "Failed to extract structured data after retries", "raw_response": result_data}, indent=2)
                    else:
                        # Should not happen if logic is correct
                        json_str = result.output.model_dump_json(indent=2)

                accumulated_response = f"```json\n{json_str}\n```"

                # Send as a single Markdown Code Block
                markdown_json = accumulated_response
                chunk_obj = {
                    "type": "content",
                    "delta": markdown_json,
                    "content": markdown_json
                }
                yield f"data: {json.dumps(chunk_obj)}\n\n"

            else:
                # Standard Chat Streaming (Text or unstructured)
                async with active_agent.run_stream(full_prompt, message_history=message_history) as result:
                    accumulated_text = ""
                    async for chunk in result.stream():
                        if isinstance(chunk, str):
                            delta = chunk
                            chunk_obj = {
                                "type": "content", 
                                "delta": delta,
                                "content": accumulated_text + delta
                            }
                            accumulated_text += delta
                            yield f"data: {json.dumps(chunk_obj)}\n\n"
                    
                    accumulated_response = accumulated_text # Capture full text

            # Save Assistant Response
            # We must use a new session or ensure thread safety? 
            # safe enough to use `SessionLocal()` here effectively.
            from database import SessionLocal
            db_sync = SessionLocal()
            try:
                asst_msg = MessageModel(
                    id=str(uuid.uuid4()),
                    chat_id=chat_id,
                    role="assistant",
                    content=accumulated_response
                )
                db_sync.add(asst_msg)
                
                # Update Chat Title if it's new and has content (First turn)
                # Maybe summarize later? For now just keep it "New Chat" or update with first few words.
                # Simplistic title update:
                chat_rec = db_sync.query(ChatModel).filter(ChatModel.id == chat_id).first()
                if chat_rec and chat_rec.title == "New Chat":
                    # Use first 30 chars of user query or assistant response? User query is better.
                    # reusing last_content_str from closure
                    new_title = last_content_str[:30] + "..." if len(last_content_str) > 30 else last_content_str
                    chat_rec.title = new_title
                
                db_sync.commit()
            except Exception as e:
                print(f"Failed to save assistant message: {e}")
            finally:
                db_sync.close()

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"AI Error: {e}")
            error_obj = {
                "type": "content",
                "delta": error_msg,
                "content": error_msg 
            }
            yield f"data: {json.dumps(error_obj)}\n\n"
            
        yield "event: end\ndata: \n\n"
    
    return StreamingResponse(stream_generator(), media_type="text/event-stream")

