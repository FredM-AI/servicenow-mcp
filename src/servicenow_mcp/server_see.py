"""
ServiceNow MCP Server - Alpic Final Version
"""
# mcp.run(transport='sse')
import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

# CONFIGURATION DES CHEMINS AVANT LES IMPORTS SERVICENOW
# On force le chemin absolu vers le fichier config pour éviter le crash dans server.py
current_dir = os.path.dirname(os.path.abspath(__file__)) # src/servicenow_mcp
project_root = os.path.abspath(os.path.join(current_dir, "..", "..")) # Racine du projet
os.environ["TOOL_PACKAGE_CONFIG_PATH"] = os.path.join(project_root, "config", "tool_packages.yaml")

from mcp.server.fastmcp import FastMCP
from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig

# Initialisation logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    # 1. Config ServiceNow
    auth_config = AuthConfig(
        type=AuthType.BASIC, 
        basic=BasicAuthConfig(
            username=os.getenv("SERVICENOW_USERNAME", ""), 
            password=os.getenv("SERVICENOW_PASSWORD", "")
        )
    )
    config = ServerConfig(
        instance_url=os.getenv("SERVICENOW_INSTANCE_URL", ""), 
        auth=auth_config
    )

    try:
        # 2. On charge votre backend (cela va lire le YAML via TOOL_PACKAGE_CONFIG_PATH)
        backend = ServiceNowMCP(config)
        
        # 3. Création de FastMCP pour Alpic
        mcp = FastMCP("ServiceNow")
        
        # 4. Bridge : On injecte votre serveur (low-level Server) dans FastMCP
        mcp._server = backend.mcp_server
        
        logger.info("✅ ServiceNow MCP Server initialized with 93 tools")
        return mcp
    except Exception as e:
        logger.error(f"💥 Crash during initialization: {e}")
        # On crée une app vide pour éviter l'Exit 128 et voir l'erreur dans les logs
        mcp_fallback = FastMCP("ServiceNow-Error")
        @mcp_fallback.tool()
        async def get_error():
            return f"Initialization Error: {str(e)}"
        return mcp_fallback

app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
