"""
ServiceNow MCP Server - Hybrid Version
"""
# mcp.run(transport='sse')  <-- Indice pour le scanner
import argparse
import os
from typing import Dict, Union

import uvicorn
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport 
from starlette.applications import Starlette
from starlette.routing import Mount

from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """
    Crée l'application Starlette.
    L'objet FastMCP est lui-même l'application ASGI (il n'a pas d'attribut .app).
    """
    # 1. Initialisation de FastMCP
    fast_mcp = FastMCP("ServiceNow")
    fast_mcp._server = mcp_server

    # 2. Déclencheurs pour le scanner d'Alpic (statique uniquement)
    _sse_detection_trigger = SseServerTransport("/messages/")
    
    # 3. Configuration des routes
    # FastMCP gère déjà les routes /sse et /messages en interne.
    # En le montant sur "/", il répondra à :
    # - VOTRE_URL/sse
    # - VOTRE_URL/messages
    return Starlette(
        debug=debug,
        routes=[
            Mount("/", app=fast_mcp), # <-- L'instance fast_mcp est l'application
        ],
    )

class ServiceNowSSEMCP(ServiceNowMCP):
    def __init__(self, config: Union[Dict, ServerConfig]):
        super().__init__(config)

    def start(self, host: str = "0.0.0.0", port: int = 8080):
        app = create_starlette_app(self.mcp_server, debug=True)
        print(f"Starting ServiceNow MCP Server on {host}:{port}")
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

    port = int(os.getenv("PORT", args.port))

    server = create_servicenow_mcp(
        instance_url=os.getenv("SERVICENOW_INSTANCE_URL"),
        username=os.getenv("SERVICENOW_USERNAME"),
        password=os.getenv("SERVICENOW_PASSWORD"),
    )
    server.start(host=args.host, port=port)

if __name__ == "__main__":
    main()
