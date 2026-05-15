from flask import Flask, request, jsonify
from datetime import datetime, timezone
import os
import logging
from telegram_service import enviar_mensaje
from database import init_db, insert_location

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Prioriza la variable de Render, si no, usa gps123 por defecto
API_KEY = os.getenv("API_KEY", "gps123")

init_db()

@app.route("/", methods=["GET"])
def home():
    return "Servidor GPS Activo", 200

@app.route("/gps", methods=["POST"])
def gps():
    try:
        data = request.get_json(force=True, silent=True)
        
        if not data or str(data.get("key")) != API_KEY:
            logger.warning("Intento de acceso con clave incorrecta")
            return "Unauthorized", 401

        dev_id = data.get("id", "AndyTracker")
        lat = round(float(data["lat"]), 6)
        lon = round(float(data["lon"]), 6)
        sat = int(data.get("sat", 0))
        ts = datetime.now(timezone.utc).strftime('%H:%M:%S')

        # Guardamos en la base de datos
        insert_location(dev_id, lat, lon, sat, ts)
        
        # Intentamos enviar a Telegram
        exito_telegram = enviar_mensaje(lat, lon, dev_id, ts, sat)
        
        if exito_telegram:
            return "Enviado OK", 200
        else:
            return "Error en Telegram", 500

    except Exception as e:
        logger.error(f"Error: {e}")
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
