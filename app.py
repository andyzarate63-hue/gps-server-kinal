from flask import Flask, request, jsonify
from datetime import datetime, timezone
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
API_KEY = os.getenv("API_KEY")

init_db()

# =========================================================
# VALIDACIÓN
# =========================================================
def validar_datos(data):

    if not data:
        return False, "No JSON"

    required = ["id", "lat", "lon", "key"]

    for field in required:
        if field not in data:
            return False, f"Falta {field}"

    # API KEY
    if data.get("key") != API_KEY:
        return False, "API KEY inválida"

    # Coordenadas numéricas
    try:
        lat = float(data["lat"])
        lon = float(data["lon"])
    except ValueError:
        return False, "Lat/Lon inválidos"

    # Rangos GPS reales
    if not (-90 <= lat <= 90):
        return False, "Latitud fuera de rango"

    if not (-180 <= lon <= 180):
        return False, "Longitud fuera de rango"

    return True, ""


# =========================================================
# DUPLICADOS
# =========================================================
def es_duplicado(device_id, lat, lon):

    last = get_last_location(device_id)

    if not last:
        return False

    last_lat, last_lon, _, _ = last

    # Aproximadamente 5 metros
    if abs(last_lat - lat) < 0.00005 and abs(last_lon - lon) < 0.00005:
        return True

    return False


# =========================================================
# HOME
# =========================================================
@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "online",
        "service": "GPS Tracker API"
    }), 200


# =========================================================
# GPS
# =========================================================
@app.route("/gps", methods=["POST"])
def gps():

    try:

        data = request.get_json()

        ok, error = validar_datos(data)

        if not ok:
            return jsonify({"error": error}), 400

        device_id = str(data["id"]).strip()

        lat = round(float(data["lat"]), 6)
        lon = round(float(data["lon"]), 6)

        sat = int(data.get("sat", 0))

        timestamp = datetime.now(timezone.utc).isoformat()

        # Evitar duplicados
        if es_duplicado(device_id, lat, lon):
            return jsonify({
                "status": "ignored_duplicate"
            }), 200

        # Guardar en DB
        insert_location(device_id, lat, lon, sat, timestamp)

        # Telegram
        if BOT_TOKEN and CHAT_ID:
            enviar_mensaje(
                lat=lat,
                lon=lon,
                device_id=device_id,
                timestamp=timestamp
            )

        return jsonify({
            "status": "ok",
            "device_id": device_id,
            "lat": lat,
            "lon": lon,
            "sat": sat,
            "timestamp": timestamp
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# ÚLTIMA UBICACIÓN
# =========================================================
@app.route("/last/<device_id>", methods=["GET"])
def last_location(device_id):

    try:

        last = get_last_location(device_id)

        if not last:
            return jsonify({
                "error": "No data"
            }), 404

        lat, lon, sat, timestamp = last

        return jsonify({
            "device_id": device_id,
            "lat": lat,
            "lon": lon,
            "sat": sat,
            "last_seen": timestamp,
            "map": f"https://maps.google.com/?q={lat},{lon}"
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# HISTORIAL
# =========================================================
@app.route("/history/<device_id>", methods=["GET"])
def history(device_id):

    try:

        limit = request.args.get("limit", 50)

        try:
            limit = int(limit)
        except ValueError:
            limit = 50

        # Máximo permitido
        limit = min(limit, 500)

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
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# STATUS
# =========================================================
@app.route("/status/<device_id>", methods=["GET"])
def status(device_id):

    try:

        last_seen = get_last_seen(device_id)

        if not last_seen:
            return jsonify({
                "device_id": device_id,
                "status": "offline"
            }), 404

        last_time = datetime.fromisoformat(last_seen)
        now = datetime.now(timezone.utc)

        diff = (now - last_time).total_seconds()

        state = "online" if diff < 60 else "offline"

        return jsonify({
            "device_id": device_id,
            "status": state,
            "last_seen": last_seen,
            "seconds_since_last": int(diff)
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=80
    )
