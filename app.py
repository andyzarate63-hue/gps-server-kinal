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
    return jsonify({"status": "online", "message": "Servidor GPS Kinal Activo"}), 200

@app.route("/gps", methods=["POST"])
def gps():
    try:
        data = request.get_json(force=True, silent=True) or request.form.to_dict()
        
        if not data or str(data.get("key")) != API_KEY:
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        device_id = str(data.get("id", "andy_tracker")).strip()
        lat, lon = round(float(data["lat"]), 6), round(float(data["lon"]), 6)
        sat = int(data.get("sat", 0))
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        # Filtro de duplicados
        last = get_last_location(device_id)
        if last and abs(last[0] - lat) < 0.0001 and abs(last[1] - lon) < 0.0001:
            return jsonify({"status": "ignored"}), 200

        insert_location(device_id, lat, lon, sat, timestamp)
        telegram_ok = enviar_mensaje(lat, lon, device_id, timestamp, sat)
        
        return jsonify({"status": "success", "telegram": telegram_ok}), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
