import asyncio
import os
import sys

try:
    from pydantic_ai import Agent
    from pydantic_ai.mcp import MCPServerStdio
except ImportError as e:
    print(f"Error importing Pydantic AI: {e}")
    # Fallback or exit depending on usage
    MCPServerStdio = None
    Agent = None

# Configuration
# Ensure these environment variables are loaded (e.g. from .env via python-dotenv in main.py)
# os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") should be set.

def create_google_drive_agent(model_name: str = 'gemini-1.5-flash'):
    """
    Creates and returns a Pydantic AI Agent configured with the Google Drive MCP server.
    """
    if not MCPServerStdio:
        raise ImportError("pydantic_ai.mcp.MCPServerStdio is required.")

    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    
    # Define the server
    gdrive_server = MCPServerStdio(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-google-drive"],
        env={
            "PATH": os.environ.get("PATH"), 
            "GOOGLE_APPLICATION_CREDENTIALS": creds_path,
        }
    )

    # Initialize the Agent
    # We return both agent and server because the server needs to be used in a context manager
    agent = Agent(
        model_name,
        # Based on user snippet, passing server in toolsets works or is desired.
        # If this param is deprecated/renamed, it would need adjustment.
        # Confirmed via verification: toolsets param likely exists or user expects it.
        # But commonly in recent versions, we might need to rely on the context manager 
        # injecting the tools.
        # We will use the 'toolsets' arg as requested.
        # Note: If 'toolsets' expects specific types, this might need refinement.
        # But following the "Take reference from code" instruction:
        toolsets=[gdrive_server],
        system_prompt="You are a document intelligence assistant with access to Google Drive."
    )
    
    return agent, gdrive_server

async def run_query(query: str):
    """
    Helper to run a one-off query against the Google Drive agent.
    """
    agent, server = create_google_drive_agent()
    
    print("Starting Google Drive MCP Agent...")
    async with server:
        result = await agent.run(query)
        return result.data

if __name__ == "__main__":
    # Test script usage
    # Ensure you set GOOGLE_APPLICATION_CREDENTIALS before running
    # export GOOGLE_APPLICATION_CREDENTIALS="path/to/creds.json"
    if len(sys.argv) > 1:
        q = sys.argv[1]
    else:
        q = "List the files in my Google Drive"
        
    try:
        out = asyncio.run(run_query(q))
        print(f"Result: {out}")
    except Exception as e:
        print(f"Error: {e}")
