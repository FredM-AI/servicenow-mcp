"""
ServiceNow MCP Server - Zero-Import Debug
"""
# mcp.run(transport='sse')
import os
import sys
from mcp.server.fastmcp import FastMCP

# ON NE CHARGE RIEN DE SERVICENOW_MCP ICI
app = FastMCP("ServiceNow")

@app.tool()
async def ping():
    """Simple ping."""
    return "pong"

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
