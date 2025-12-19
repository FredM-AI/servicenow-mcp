"""
ServiceNow MCP Server - FastMCP Clean Version
"""
# mcp.run(transport='sse')  <-- Indice crucial pour le scanner Alpic
import os
import sys
import logging
from dotenv import load_dotenv

# Configuration du logging pour voir l'erreur dans la console Alpic
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from mcp.server.fastmcp import FastMCP
    from servicenow_mcp.server import ServiceNowMCP
    from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig
except ImportError as e:
    logger.error(f"❌ Erreur d'importation : {e}")
    sys.exit(1)

def create_app():
    load_dotenv()
    
    # Vérification des variables d'env essentielles pour éviter le crash
    instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
    if not instance_url:
        logger.error("❌ SERVICENOW_INSTANCE_URL est manquante !")
        # On ne sys.exit pas ici pour laisser le serveur démarrer et afficher l'erreur
    
    # 1. Initialisation de la config
    auth_config = AuthConfig(
        type=AuthType.BASIC, 
        basic=BasicAuthConfig(
            username=os.getenv("SERVICENOW_USERNAME", ""), 
            password=os.getenv("SERVICENOW_PASSWORD", "")
        )
    )
    config = ServerConfig(instance_url=instance_url, auth=auth_config)

    # 2. Chargement de vos outils ServiceNow existants
    logger.info("⏳ Loading ServiceNow MCP Tools (93 tools)...")
    try:
        server_instance = ServiceNowMCP(config)
    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement des outils : {e}")
        raise

    # 3. Création de l'interface FastMCP (Standard recommandé par Alpic)
    mcp = FastMCP("ServiceNow")

    # 4. BRIDGE : Injection de votre serveur initialisé dans FastMCP
    # Cela permet de garder vos 93 outils sans les réécrire
    mcp._server = server_instance.mcp_server
    
    return mcp

# L'objet 'app' est ce qu'Uvicorn va chercher
try:
    app = create_app()
    logger.info("✅ FastMCP App ready for ASGI")
except Exception as e:
    logger.error(f"💥 Fatal error during app creation: {e}")
    # On laisse l'erreur remonter pour qu'Alpic l'affiche dans les logs
    raise

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    # Utilisation de l'import string pour éviter des problèmes de sérialisation
    uvicorn.run("servicenow_mcp.server_see:app", host="0.0.0.0", port=port, log_level="info")
