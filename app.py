from flask import Flask, request, jsonify
from datetime import datetime
import os
from telegram_service import enviar_mensaje
from database import init_db, insert_location, get_history

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

init_db()

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


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online"}), 200


# ===================== GPS INPUT =====================
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

        # 🔥 1. GUARDAR EN BASE DE DATOS (NUEVO)
        insert_location(device_id, lat, lon, sat, timestamp)

        # 🔥 2. TELEGRAM
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


# ===================== HISTORIAL (NUEVO) =====================
@app.route("/history/<device_id>", methods=["GET"])
def history(device_id):

    limit = request.args.get("limit", 50)

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
