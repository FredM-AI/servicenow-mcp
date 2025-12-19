"""
ServiceNow MCP Server

This module provides the main implementation of the ServiceNow MCP server
using FastMCP for robust SSE transport handling.
"""
import argparse
import os
from typing import Dict, Union

import uvicorn
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount

from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """
    Crée une application Starlette via FastMCP.
    
    Cette approche utilise le transport SSE haut niveau recommandé par le SDK
    et résout les problèmes de synchronisation (race conditions).
    """
    # 1. On initialise FastMCP
    fast_mcp = FastMCP("ServiceNow")

    # 2. On lie votre serveur MCP existant (contenant vos outils) à FastMCP.
    # Cela permet de garder votre logique ServiceNowMCP intacte.
    fast_mcp._server = mcp_server

    # 3. CRITIQUE : On retourne l'application ASGI interne de FastMCP (.app)
    # C'est ce qui corrige l'erreur "FastMCP object is not callable".
    return fast_mcp.app


class ServiceNowSSEMCP(ServiceNowMCP):
    """
    Implémentation du serveur ServiceNow MCP avec transport SSE via FastMCP.
    """

    def __init__(self, config: Union[Dict, ServerConfig]):
        super().__init__(config)

    def start(self, host: str = "0.0.0.0", port: int = 8080):
        """
        Démarre le serveur Uvicorn avec l'application FastMCP.
        """
        # On crée l'application Starlette/FastMCP
        app = create_starlette_app(self.mcp_server, debug=True)

        print(f"Starting ServiceNow MCP Server on {host}:{port}")
        
        # On lance Uvicorn directement sur l'application
        uvicorn.run(app, host=host, port=port)


def create_servicenow_mcp(instance_url: str, username: str, password: str):
    """
    Factory function pour configurer le serveur.
    """
    auth_config = AuthConfig(
        type=AuthType.BASIC, 
        basic=BasicAuthConfig(username=username, password=password)
    )

    config = ServerConfig(instance_url=instance_url, auth=auth_config)

    return ServiceNowSSEMCP(config)


def main():
    """
    Point d'entrée principal.
    """
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run ServiceNow MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()

    # Alpic définit souvent la variable d'environnement PORT
    server_port = int(os.getenv("PORT", args.port))

    server = create_servicenow_mcp(
        instance_url=os.getenv("SERVICENOW_INSTANCE_URL"),
        username=os.getenv("SERVICENOW_USERNAME"),
        password=os.getenv("SERVICENOW_PASSWORD"),
    )
    
    server.start(host=args.host, port=server_port)


if __name__ == "__main__":
    main()
