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

# ... imports ...
from services.agent import agent, model
from typing import Union
from pydantic_ai import Agent

from database import get_db, File as FileModel
from sqlalchemy.orm import Session
from fastapi import Depends
import re
import os

from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, UserPromptPart
from services.vector_store import vector_store
from prompts.industries import INDUSTRY_PROMPTS

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
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
        try:
            # Determine if we are in STRICT Extraction Mode (Banking)
            is_strict_extraction = request.industry == "banking"

            if is_strict_extraction:
                # Non-streaming execution for Strict Extraction
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

                # Send as a single Markdown Code Block
                markdown_json = f"```json\n{json_str}\n```"
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

