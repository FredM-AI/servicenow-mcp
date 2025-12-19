"""
ServiceNow MCP Server - FastMCP Clean Version
"""
# mcp.run(transport='sse')
import os
from mcp.server.fastmcp import FastMCP
from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig
from dotenv import load_dotenv

load_dotenv()

def create_mcp_app():
    # 1. Configuration ServiceNow
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

    # 2. On charge vos outils existants (les 93 outils)
    # Important : ServiceNowMCP doit être instancié avant de créer l'app FastMCP
    service_now_backend = ServiceNowMCP(config)

    # 3. Création de l'application FastMCP demandée par Alpic
    mcp = FastMCP("ServiceNow")

    # 4. Bridge : On injecte votre serveur initialisé dans FastMCP
    # Cela évite de devoir ré-enregistrer chaque outil manuellement
    mcp._server = service_now_backend.mcp_server
    
    return mcp

# L'objet 'app' est ce qu'Alpic va chercher via Uvicorn
app = create_mcp_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
