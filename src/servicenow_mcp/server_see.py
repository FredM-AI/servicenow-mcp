"""
ServiceNow MCP Server

This module provides the main implementation of the ServiceNow MCP server,
now using FastMCP for robust SSE transport handling.
"""
# mcp.run(transport='sse')
import argparse
import os
from typing import Dict, Union

import uvicorn
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.fastmcp import FastMCP # <-- CONSERVÉ
from starlette.applications import Starlette
from starlette.routing import Mount, Route # Conserver Route si d'autres routes sont nécessaires

from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """
    Create a Starlette application that serves the provided mcp server using FastMCP.
    
    FastMCP handles the /sse, /messages, and /v1 routes automatically, solving 
    the synchronization issues encountered with manual SSE setup.
    """
    
    # [MODIFICATION CRITIQUE] Utiliser FastMCP pour encapsuler le serveur MCP
    fast_mcp_app = FastMCP(mcp_server) 

    # L'application Starlette principale monte FastMCP à la racine.
    return Starlette(
        debug=debug,
        routes=[
            # FastMCP gère désormais tout le protocole à partir de la racine (/)
            Mount("/", app=fast_mcp_app),
        ],
    )


class ServiceNowSSEMCP(ServiceNowMCP):
    """
    ServiceNow MCP Server implementation.

    This class provides a Model Context Protocol (MCP) server for ServiceNow,
    allowing LLMs to interact with ServiceNow data and functionality.
    """

    def __init__(self, config: Union[Dict, ServerConfig]):
        """
        Initialize the ServiceNow MCP server.

        Args:
            config: Server configuration, either as a dictionary or ServerConfig object.
        """
        super().__init__(config)

    def start(self, host: str = "0.0.0.0", port: int = 8080):
        """
        Start the MCP server with SSE transport using Starlette and Uvicorn.

        Args:
            host: Host address to bind to
            port: Port to listen on
        """
        # Create Starlette app using FastMCP transport
        starlette_app = create_starlette_app(self.mcp_server, debug=True)

        # Run using uvicorn
        uvicorn.run(starlette_app, host=host, port=port)


def create_servicenow_mcp(instance_url: str, username: str, password: str):
    """
    Create a ServiceNow MCP server with minimal configuration.

    This is a simplified factory function that creates a pre-configured
    ServiceNow MCP server with basic authentication.

    Args:
        instance_url: ServiceNow instance URL
        username: ServiceNow username
        password: ServiceNow password

    Returns:
        A configured ServiceNowMCP instance ready to use
    """

    # Create basic auth config
    auth_config = AuthConfig(
        type=AuthType.BASIC, basic=BasicAuthConfig(username=username, password=password)
    )

    # Create server config
    config = ServerConfig(instance_url=instance_url, auth=auth_config)

    # Create and return server
    return ServiceNowSSEMCP(config)


def main():
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run ServiceNow MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()

    server = create_servicenow_mcp(
        instance_url=os.getenv("SERVICENOW_INSTANCE_URL"),
        username=os.getenv("SERVICENOW_USERNAME"),
        password=os.getenv("SERVICENOW_PASSWORD"),
    )
    server.start(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
