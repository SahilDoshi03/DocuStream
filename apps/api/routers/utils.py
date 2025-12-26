import json
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import Message as MessageModel

def get_latest_valid_extraction(db: Session, chat_id: str):
    """
    Retrieves the latest valid extracted JSON data from the assistant's message history.
    Iterates backwards through messages to find the most recent successful extraction.
    """
    # Get all assistant messages ordered by time (descending)
    messages = db.query(MessageModel).filter(
        MessageModel.chat_id == chat_id,
        MessageModel.role == "assistant"
    ).order_by(desc(MessageModel.created_at)).all()
    
    for msg in messages:
        content = msg.content
        if not content:
            continue
        
        # Check if content looks like JSON or Markdown JSON
        try:
            json_str = ""
            if "```json" in content:
                # Extract JSON block
                start = content.find("```json") + 7
                end = content.find("```", start)
                if end == -1:
                    # Maybe it ends at the end of string
                    json_str = content[start:].strip()
                else:
                    json_str = content[start:end].strip()
            elif content.strip().startswith("{") and content.strip().endswith("}"):
                json_str = content.strip()
            
            if json_str:
                data = json.loads(json_str)
                # Basic validation: check for key extraction fields like 'customer' or 'banking'
                # or just verify it's a dict
                if isinstance(data, dict):
                    # We assume if it parses as JSON object it might be our extraction.
                    # Ideally strict check, but for now this suffices.
                    return data
        except Exception:
            # Not valid valid JSON, continue to next message
            continue
    
    return None
