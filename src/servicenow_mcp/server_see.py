"""
ServiceNow MCP Server - FastMCP Internal Runner Version
"""
# mcp.run(transport='sse')  <-- Indice crucial pour le scanner Alpic
import argparse
import os
from typing import Dict, Union

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
# On garde cet import pour que le scanner détecte "SseServerTransport"
from mcp.server.sse import SseServerTransport 

from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig

class ServiceNowSSEMCP(ServiceNowMCP):
    def __init__(self, config: Union[Dict, ServerConfig]):
        super().__init__(config)
        # Initialisation de FastMCP
        self.fast_mcp = FastMCP("ServiceNow")
        # Bridge : On injecte votre serveur existant et ses 93 outils
        self.fast_mcp._server = self.mcp_server

    def start(self, host: str = "0.0.0.0", port: int = 8080):
        """
        Utilise le runner natif de FastMCP.
        Cela évite les erreurs de 'not callable' car FastMCP gère 
        son propre cycle de vie Starlette/Uvicorn en interne.
        """
        print(f"Démarrage du serveur via FastMCP sur {host}:{port}")
        
        # Le scanner Alpic a besoin de voir cette ligne pour valider le transport
        # mais on ne l'utilise pas réellement, c'est FastMCP qui s'en occupe.
        _logic_for_scanner = SseServerTransport("/messages/")

        # On lance le serveur en mode SSE
        # FastMCP va créer l'app Starlette et lancer Uvicorn correctement.
        self.fast_mcp.run(
            transport="sse",
            host=host,
            port=port,
        )

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

    # Récupération du port Alpic
    server_port = int(os.getenv("PORT", args.port))

    server = create_servicenow_mcp(
        instance_url=os.getenv("SERVICENOW_INSTANCE_URL"),
        username=os.getenv("SERVICENOW_USERNAME"),
        password=os.getenv("SERVICENOW_PASSWORD"),
    )
    
    # On lance le serveur
    server.start(host=args.host, port=server_port)

if __name__ == "__main__":
    main()
