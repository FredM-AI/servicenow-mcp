"""
ServiceNow MCP Server - FastMCP Version
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
    Crée l'application Starlette en utilisant le bridge FastMCP.
    """
    # 1. On initialise FastMCP avec un nom (obligatoire)
    # Note: FastMCP ne prend pas un objet Server en argument, on l'initialise normalement.
    fast_mcp = FastMCP("ServiceNow")

    # 2. [BRIDGE] On lie votre mcp_server existant (avec ses 93 outils) à FastMCP
    # C'est une astuce pour garder vos outils tout en utilisant le transport de FastMCP
    fast_mcp._server = mcp_server

    # 3. L'application ASGI réelle attendue par Starlette est fast_mcp.app
    return Starlette(
        debug=debug,
        routes=[
            Mount("/", app=fast_mcp.app), # <-- LA CORRECTION EST ICI (.app)
        ],
    )

class ServiceNowSSEMCP(ServiceNowMCP):
    def __init__(self, config: Union[Dict, ServerConfig]):
        super().__init__(config)

    def start(self, host: str = "0.0.0.0", port: int = 8080):
        # On crée l'application Starlette via le bridge FastMCP
        starlette_app = create_starlette_app(self.mcp_server, debug=True)
        
        print(f"Starting Uvicorn on {host}:{port}")
        uvicorn.run(starlette_app, host=host, port=port)

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

    # Récupération du port depuis l'environnement Alpic (prioritaire)
    env_port = int(os.getenv("PORT", args.port))

    server = create_servicenow_mcp(
        instance_url=os.getenv("SERVICENOW_INSTANCE_URL"),
        username=os.getenv("SERVICENOW_USERNAME"),
        password=os.getenv("SERVICENOW_PASSWORD"),
    )
    server.start(host=args.host, port=env_port)

if __name__ == "__main__":
    main()
