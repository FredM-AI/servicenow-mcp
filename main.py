#!/usr/bin/env python3
"""
Point d'entrée pour démarrer le serveur MCP ServiceNow en mode SSE
"""
import os
import uvicorn
from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.server_sse import create_starlette_app
from servicenow_mcp.utils.config import ServerConfig, AuthConfig, AuthType, BasicAuthConfig

def main():
    # Configuration depuis les variables d'environnement
    config = ServerConfig(
        instance_url=os.getenv("SERVICENOW_INSTANCE_URL"),
        auth=AuthConfig(
            type=AuthType.BASIC,
            config=BasicAuthConfig(
                username=os.getenv("SERVICENOW_USERNAME"),
                password=os.getenv("SERVICENOW_PASSWORD")
            )
        ),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )
    
    # Créer le serveur MCP
    servicenow_mcp = ServiceNowMCP(config)
    
    # Créer l'application Starlette avec transport SSE
    app = create_starlette_app(servicenow_mcp, debug=True)
    
    # Démarrer le serveur
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
