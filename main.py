# main.py

# Ceci exécute le script d'entrée que nous avons installé via pip install -e .
import subprocess
import sys
import os

# Récupérer le port configuré par Alpic, par défaut à 8080
port = os.getenv("PORT", "8080")

print(f"Starting servicenow-mcp-sse server on 0.0.0.0:{port}")

# Exécuter la commande SSE
try:
    subprocess.run(["servicenow-mcp-sse", f"--host=0.0.0.0", f"--port={port}"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error during server start: {e}")
    sys.exit(1)
