import os
from dotenv import load_dotenv

# Explicitly load .env from current directory
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class Config:
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Replicate (Legacy/Optional)
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

    # NotebookLM (MCP)
    # The MCP server command. Usually 'uvx' or 'npx' or direct executable if installed via pipx
    # We default to 'uvx notebooklm-mcp-server' assuming uv is installed, or just 'notebooklm-mcp-server'
    NOTEBOOKLM_MCP_COMMAND = os.getenv("NOTEBOOKLM_MCP_COMMAND", "notebooklm-mcp-server") 
    
    # Fireflies.ai
    FIREFLIES_API_KEY = os.getenv("FIREFLIES_API_KEY")
    FIREFLIES_GRAPHQL_URL = "https://api.fireflies.ai/graphql"

    # Paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "resources", "uploads")
