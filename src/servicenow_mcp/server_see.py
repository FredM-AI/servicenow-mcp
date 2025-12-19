import os
import logging
from dotenv import load_dotenv
import uvicorn

from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.server_sse import create_starlette_app
from servicenow_mcp.utils.config import (
    ServerConfig,
    AuthConfig,
    AuthType,
    BasicAuthConfig,
)

load_dotenv()
logging.basicConfig(level=logging.INFO)

def create_app():
    config = ServerConfig(
        instance_url=os.environ["SERVICENOW_INSTANCE_URL"],
        auth=AuthConfig(
            type=AuthType.BASIC,
            config=BasicAuthConfig(
                username=os.environ["SERVICENOW_USERNAME"],
                password=os.environ["SERVICENOW_PASSWORD"],
            ),
        ),
        debug=True,
    )

    backend = ServiceNowMCP(config)

    # 🔥 LE POINT CLÉ : on passe le MCP Server interne
    mcp_server = backend.mcp_server

    app = create_starlette_app(mcp_server, debug=True)
    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
