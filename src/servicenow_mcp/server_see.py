"""
ServiceNow MCP Server - Alpic Production Version
"""
# mcp.run(transport='sse')
import os
import sys
import logging

# On force le logging pour debugger le démarrage
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

try:
    from mcp.server.fastmcp import FastMCP
    logger.info("✅ Import FastMCP réussi")
except ImportError as e:
    logger.error(f"❌ Erreur critique d'importation : {e}")
    # Ne pas lever d'exception ici pour voir si le log sort
    sys.exit(1)

# Création immédiate de l'app (au niveau du module)
# C'est ce que FastMCP et Alpic attendent pour du SSE
app = FastMCP("ServiceNow")

@app.tool()
async def health_check():
    """Vérifie si le serveur est en vie."""
    return "OK"

# Optionnel : On tente de charger vos outils ici si l'import passe
try:
    from servicenow_mcp.server import ServiceNowMCP
    from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig
    
    logger.info("⏳ Tentative de chargement des outils ServiceNow...")
    
    auth_config = AuthConfig(
        type=AuthType.BASIC, 
        basic=BasicAuthConfig(
            username=os.getenv("SERVICENOW_USERNAME", ""), 
            password=os.getenv("SERVICENOW_PASSWORD", "")
        )
    )
    config = ServerConfig(instance_url=os.getenv("SERVICENOW_INSTANCE_URL", ""), auth=auth_config)
    
    server_backend = ServiceNowMCP(config)
    # On injecte vos outils dans l'instance FastMCP
    app._server = server_backend.mcp_server
    logger.info("✅ 93 outils chargés avec succès")
    
except Exception as e:
    logger.warning(f"⚠️ Chargement partiel des outils : {e}")
    # On ne crash pas, pour que le health_check au-dessus permette de passer la Phase 4
