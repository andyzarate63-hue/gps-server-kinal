from flask import Flask
import os
import logging

# Configuración básica de logs para monitorear el servidor en Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    """
    Página principal que confirma que el servicio está activo.
    El ESP32 ahora opera de forma independiente vía Telegram.
    """
    logger.info("Servidor consultado.")
    return "Servidor GPS en modo pasivo. Sistema operando de forma independiente vía Telegram.", 200

@app.route("/ping", methods=["GET"])
def ping():
    """Endpoint de salud para que Render sepa que el servicio está vivo."""
    return "OK", 200

if __name__ == "__main__":
    # Render asigna el puerto automáticamente mediante variables de entorno
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
