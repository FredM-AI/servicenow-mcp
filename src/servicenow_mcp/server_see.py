"""
ServiceNow MCP Server - Minimal Debug Version
"""
# mcp.run(transport='sse')
import os
import logging
from mcp.server.fastmcp import FastMCP

# Configuration du log pour forcer l'affichage dans Alpic
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("🚀 Démarrage du script server_see.py")

try:
    # On crée une instance FastMCP vide (sans charger vos 93 outils pour l'instant)
    # Cela permet de vérifier si le transport SSE et la config Alpic sont OK.
    app = FastMCP("ServiceNow")

    @app.tool()
    async def ping():
        """Outil de test minimal pour valider la connectivité."""
        return "pong"

    logger.info("✅ Application FastMCP (Debug) initialisée")

except Exception as e:
    logger.error(f"❌ Erreur fatale : {e}")
    raise

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
