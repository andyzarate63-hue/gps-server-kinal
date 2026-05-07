from flask import Flask, request, jsonify
from datetime import datetime
import os

from telegram_service import enviar_mensaje
from database import (
    init_db,
    insert_location,
    get_history,
    get_last_location,
    get_last_seen
)

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

init_db()

# ================= VALIDACIÓN =================
def validar_datos(data):
    if not data:
        return False, "No JSON"

    if "id" not in data:
        return False, "Falta device_id"

    if "lat" not in data or "lon" not in data:
        return False, "Faltan coordenadas"

    try:
        float(data["lat"])
        float(data["lon"])
    except:
        return False, "Lat/Lon inválidos"

    return True, ""


# ================= DUPLICADOS =================
def es_duplicado(device_id, lat, lon):
    last = get_last_location(device_id)

    if not last:
        return False

    last_lat, last_lon = last[0], last[1]

    if abs(last_lat - lat) < 0.00005 and abs(last_lon - lon) < 0.00005:
        return True

    return False


# ================= HOME =================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online"}), 200


# ================= GPS =================
@app.route("/gps", methods=["POST"])
def gps():

    try:
        data = request.get_json()

        ok, error = validar_datos(data)
        if not ok:
            return jsonify({"error": error}), 400

        device_id = data["id"]
        lat = float(data["lat"])
        lon = float(data["lon"])
        sat = data.get("sat", 0)
        timestamp = datetime.utcnow().isoformat()

        if es_duplicado(device_id, lat, lon):
            return jsonify({"status": "ignored_duplicate"}), 200

        insert_location(device_id, lat, lon, sat, timestamp)

        if BOT_TOKEN and CHAT_ID:
            enviar_mensaje(lat, lon, device_id, timestamp)

        return jsonify({
            "status": "ok",
            "id": device_id,
            "lat": lat,
            "lon": lon,
            "sat": sat,
            "time": timestamp
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= ÚLTIMA UBICACIÓN =================
@app.route("/last/<device_id>", methods=["GET"])
def last_location(device_id):

    last = get_last_location(device_id)
    seen = get_last_seen(device_id)

    if not last:
        return jsonify({"error": "no data"}), 404

    lat, lon, sat, timestamp = last

    return jsonify({
        "device_id": device_id,
        "lat": lat,
        "lon": lon,
        "sat": sat,
        "last_seen": seen,
        "map": f"https://maps.google.com/?q={lat},{lon}"
    })


# ================= HISTORIAL =================
@app.route("/history/<device_id>", methods=["GET"])
def history(device_id):

    limit = int(request.args.get("limit", 50))

    data = get_history(device_id, limit)

    return jsonify({
        "device_id": device_id,
        "count": len(data),
        "history": [
            {
                "lat": row[0],
                "lon": row[1],
                "sat": row[2],
                "timestamp": row[3]
            }
            for row in data
        ]
    })


# ================= STATUS =================
@app.route("/status/<device_id>", methods=["GET"])
def status(device_id):

    last_seen = get_last_seen(device_id)

    if not last_seen:
        return jsonify({"status": "offline"}), 404

    last_time = datetime.fromisoformat(last_seen)
    now = datetime.utcnow()

    diff = (now - last_time).total_seconds()

    state = "online" if diff < 60 else "offline"

    return jsonify({
        "device_id": device_id,
        "status": state,
        "last_seen": last_seen,
        "seconds_since_last": diff
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
