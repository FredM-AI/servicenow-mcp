# main.py

# Ceci exécute le script d'entrée que nous avons installé via pip install -e .
# import subprocess
# import sys
# import os

# Récupérer le port configuré par Alpic, par défaut à 8080
#port = os.getenv("PORT", "8080")

#print(f"Starting servicenow-mcp-sse server on 0.0.0.0:{port}")

# Exécuter la commande SSE
#try:
#    subprocess.run(["servicenow-mcp-sse", f"--host=0.0.0.0", f"--port={port}"], check=True)
#except subprocess.CalledProcessError as e:
#    print(f"Error during server start: {e}")
#    sys.exit(1)
    
# main.py (Version Corrigée)

# Importe la fonction main() que nous avons définie dans server_sse.py
# Le chemin doit correspondre à la structure de votre projet : src/servicenow_mcp/server_sse.py
from servicenow_mcp.server_sse import main 

# Le script `main.py` appelle directement la fonction principale du serveur
if __name__ == "__main__":
    # La fonction main() dans server_sse.py gère déjà la récupération du port
    # et le lancement d'uvicorn.
    print("Starting ServiceNow MCP Server directly via internal main() function.")
    main()
