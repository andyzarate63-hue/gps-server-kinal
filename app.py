from flask import Flask, request, jsonify
from datetime import datetime, timezone
import os, logging
from telegram_service import enviar_mensaje
from database import init_db, insert_location, get_last_location

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
API_KEY = "gps123" # Sincronizado con Arduino

init_db()

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online", "project": "GPS Kinal"}), 200

@app.route("/gps", methods=["POST"])
def gps():
    try:
        data = request.get_json(force=True, silent=True)
        if not data or data.get("key") != API_KEY:
            return jsonify({"status": "denied"}), 401

        dev_id = data.get("id", "AndyTracker")
        lat, lon = round(float(data["lat"]), 6), round(float(data["lon"]), 6)
        sat = int(data.get("sat", 0))
        ts = datetime.now(timezone.utc).strftime('%H:%M:%S')

        last = get_last_location(dev_id)
        if last and abs(last[0] - lat) < 0.0001 and abs(last[1] - lon) < 0.0001:
            return jsonify({"status": "static"}), 200

        insert_location(dev_id, lat, lon, sat, ts)
        telegram_ok = enviar_mensaje(lat, lon, dev_id, ts, sat)
        
        return jsonify({"status": "success", "telegram": telegram_ok}), 200
    except Exception as e:
        logger.error(f"Fail: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
