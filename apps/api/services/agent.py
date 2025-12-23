from pydantic_ai import Agent
import os
from dotenv import load_dotenv

load_dotenv()

system_prompt = """You are DocuStream AI, an intelligent assistant that helps users analyze documents.
You will be provided with context from uploaded files (PDFs, etc.). 
Use this context to answer the user's questions accurately.
If the answer is not in the context, say so.
Always be helpful, concise, and professional.
"""

gemini_key = os.getenv("GEMINI_API_KEY")
llm_model_env = os.getenv("LLM_MODEL")

if gemini_key:
    from pydantic_ai.models.google import GoogleModel
    from pydantic_ai.providers.google import GoogleProvider
    
    # User requested 1.5 Flash (Free Tier). 'gemini-flash-latest' usually points to this.
    print(f"Initializing Gemini Agent with model: gemini-flash-latest")
    provider = GoogleProvider(api_key=gemini_key)
    model = GoogleModel('gemini-flash-latest', provider=provider)
    agent = Agent(model, system_prompt=system_prompt)

elif llm_model_env:
    # Fallback to string based initialization (e.g. OpenAI)
    print(f"Initializing Agent with model: {llm_model_env}")
    agent = Agent(llm_model_env, system_prompt=system_prompt)

else:
    # Default fallback
    print("Initializing Agent with default OpenAI model")
    agent = Agent("openai:gpt-4o", system_prompt=system_prompt)
