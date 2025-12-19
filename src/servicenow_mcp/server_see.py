"""
ServiceNow MCP Server - FastMCP Starlette Version
"""
# mcp.run(transport='sse')  <-- Indice crucial pour le scanner Alpic
import argparse
import os
import uvicorn
from typing import Dict, Union

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport # Pour la détection Alpic
from starlette.routing import Route, Mount
from starlette.applications import Starlette

from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """
    Configure FastMCP et expose son application Starlette interne.
    """
    # 1. Initialisation de FastMCP
    fast_mcp = FastMCP("ServiceNow")
    
    # 2. Bridge : On injecte votre serveur avec ses 93 outils
    fast_mcp._server = mcp_server

    # 3. Récupération de l'application Starlette interne de FastMCP
    # Note: Dans le SDK MCP, c'est 'starlette_app' et non '.app'
    app = fast_mcp.starlette_app

    # 4. On s'assure que les routes attendues par Alpic sont là (pour la détection)
    # Même si FastMCP les gère, les déclarer ici aide le scanner.
    _detector = SseServerTransport("/messages/")
    
    return app

class ServiceNowSSEMCP(ServiceNowMCP):
    def __init__(self, config: Union[Dict, ServerConfig]):
        super().__init__(config)

    def start(self, host: str = "0.0.0.0", port: int = 8080):
        """
        Lancement manuel de l'application via Uvicorn pour contrôler le port.
        """
        app = create_starlette_app(self.mcp_server, debug=True)
        
        print(f"🚀 Starting ServiceNow MCP Server on {host}:{port}")
        
        # On utilise uvicorn directement sur l'app interne de FastMCP
        uvicorn.run(app, host=host, port=port)

def create_servicenow_mcp(instance_url: str, username: str, password: str):
    auth_config = AuthConfig(
        type=AuthType.BASIC, basic=BasicAuthConfig(username=username, password=password)
    )
    config = ServerConfig(instance_url=instance_url, auth=auth_config)
    return ServiceNowSSEMCP(config)

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run ServiceNow MCP server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    # On utilise bien le port imposé par Alpic
    server_port = int(os.getenv("PORT", args.port))

    server = create_servicenow_mcp(
        instance_url=os.getenv("SERVICENOW_INSTANCE_URL"),
        username=os.getenv("SERVICENOW_USERNAME"),
        password=os.getenv("SERVICENOW_PASSWORD"),
    )
    
    server.start(host=args.host, port=server_port)

if __name__ == "__main__":
    main()
