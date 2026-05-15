from flask import Flask, request, jsonify
from datetime import datetime, timezone
import os
import logging
from telegram_service import enviar_mensaje
from database import init_db, insert_location, get_last_location

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
API_KEY = os.getenv("API_KEY", "gps123")
init_db()

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online", "msg": "Servidor GPS Activo"}), 200

@app.route("/gps", methods=["POST"])
def gps():
    try:
        # force=True permite leer el JSON aunque el cliente no mande el header correcto
        data = request.get_json(force=True, silent=True) or request.form.to_dict()
        
        if not data or str(data.get("key")) != API_KEY:
            logger.warning("Intento de acceso no autorizado")
            return jsonify({"status": "unauthorized"}), 401

        device_id = data.get("id", "andy_device")
        lat = float(data["lat"])
        lon = float(data["lon"])
        sat = int(data.get("sat", 0))
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        # Filtro de duplicados (aprox 10 metros)
        last = get_last_location(device_id)
        if last and abs(last[0] - lat) < 0.0001 and abs(last[1] - lon) < 0.0001:
            logger.info(f"📍 {device_id} estático.")
            return jsonify({"status": "ignored"}), 200

        insert_location(device_id, lat, lon, sat, timestamp)
        telegram_ok = enviar_mensaje(lat, lon, device_id, timestamp, sat)

        return jsonify({"status": "success", "telegram": telegram_ok}), 200
    except Exception as e:
        logger.error(f"Error en endpoint /gps: {e}")
        return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == "__main__":
    # Render usa el puerto 10000 por defecto
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
