"""
ServiceNow MCP Server - Official FastMCP SSE Style
"""
# mcp.run(transport='sse')  <-- Indice crucial pour le scanner Alpic
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig

load_dotenv()

# 1. Initialisation de la config ServiceNow
auth_config = AuthConfig(
    type=AuthType.BASIC, 
    basic=BasicAuthConfig(
        username=os.getenv("SERVICENOW_USERNAME"), 
        password=os.getenv("SERVICENOW_PASSWORD")
    )
)
config = ServerConfig(instance_url=os.getenv("SERVICENOW_INSTANCE_URL"), auth=auth_config)

# 2. On instancie votre serveur existant pour charger les outils
# (C'est ici que les 93 outils sont enregistrés dans server_instance.mcp_server)
print("⏳ Loading ServiceNow MCP Tools...")
server_instance = ServiceNowMCP(config)

# 3. On crée l'interface FastMCP
# On lui donne le même nom que votre serveur
mcp = FastMCP("ServiceNow")

# 4. BRIDGE CRUCIAL : On remplace le serveur interne de FastMCP par le vôtre 
# qui contient déjà tous les outils chargés.
mcp._server = server_instance.mcp_server

# 5. Point d'entrée pour Alpic/Uvicorn
# FastMCP est compatible ASGI, donc on peut l'exposer directement.
app = mcp

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Starting FastMCP Server on port {port}")
    # On lance l'objet 'mcp' directement car il est 'callable' (ASGI app)
    uvicorn.run("server_see:app", host="0.0.0.0", port=port, factory=False)
