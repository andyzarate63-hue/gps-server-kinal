from flask import Flask, request, jsonify
from datetime import datetime, timezone
import os
import logging

# Importaciones locales
from telegram_service import enviar_mensaje
from database import (
    init_db,
    insert_location,
    get_last_location
)

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# La API_KEY debe ser la misma que pongas en el ESP32
API_KEY = os.getenv("API_KEY", "gps123")

# Inicializar base de datos al arrancar
init_db()

def es_duplicado(device_id, lat, lon):
    """ Evita guardar si la ubicación es casi la misma (dispositivo quieto) """
    last = get_last_location(device_id)
    if not last:
        return False
    # Tolerancia de aproximadamente 10 metros
    return abs(last[0] - lat) < 0.0001 and abs(last[1] - lon) < 0.0001

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online", "message": "Servidor GPS Kinal Activo"}), 200

@app.route("/gps", methods=["POST"])
def gps():
    try:
        # force=True permite leer el JSON aunque el cliente no mande headers perfectos
        data = request.get_json(force=True, silent=True) or request.form.to_dict()
        
        if not data or str(data.get("key")) != API_KEY:
            logger.warning("Intento de acceso no autorizado")
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        device_id = str(data.get("id", "andy_device")).strip()
        lat = round(float(data["lat"]), 6)
        lon = round(float(data["lon"]), 6)
        sat = int(data.get("sat", 0))
        
        now = datetime.now(timezone.utc)
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        # Si no se ha movido, respondemos OK pero no hacemos nada más
        if es_duplicado(device_id, lat, lon):
            return jsonify({"status": "ignored", "reason": "static"}), 200

        # Guardar en base de datos
        insert_location(device_id, lat, lon, sat, timestamp)
        
        # Enviar a Telegram
        telegram_ok = enviar_mensaje(lat, lon, device_id, timestamp, sat)
        
        logger.info(f"✅ Datos procesados para {device_id}")
        return jsonify({"status": "success", "telegram": telegram_ok}), 200

    except Exception as e:
        logger.error(f"❌ Error crítico: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
