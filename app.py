from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Faltan variables de entorno (BOT_TOKEN o CHAT_ID)")

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# ================= FUNCIONES =================

def log(msg):
    print(f"[{datetime.now()}] {msg}")

def validar_datos(data):
    if not isinstance(data, dict):
        return False, "JSON inválido"

    if "lat" not in data or "lon" not in data:
        return False, "Faltan campos obligatorios"

    try:
        lat = float(data["lat"])
        lon = float(data["lon"])
    except:
        return False, "Datos no numéricos"

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return False, "Coordenadas fuera de rango"

    return True, ""

def enviar_telegram(lat, lon):
    mensaje = (
        f"📍 GPS ESP32\n"
        f"Lat: {lat}\n"
        f"Lon: {lon}\n"
        f"https://maps.google.com/?q={lat},{lon}"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje
    }

    response = requests.post(
        TELEGRAM_URL,
        json=payload,
        timeout=10
    )

    return response.status_code == 200

# ================= RUTAS =================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "GPS Tracker API"
    }), 200


@app.route("/gps", methods=["POST"])
def recibir_gps():
    try:
        data = request.get_json()

        valido, error = validar_datos(data)
        if not valido:
            log(f"Error validación: {error}")
            return jsonify({"error": error}), 400

        lat = float(data["lat"])
        lon = float(data["lon"])

        log(f"Datos recibidos: {lat}, {lon}")

        if not enviar_telegram(lat, lon):
            log("Error enviando a Telegram")
            return jsonify({"error": "Fallo Telegram"}), 500

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        log(f"Error interno: {str(e)}")
        return jsonify({"error": "Error interno"}), 500


# ================= MAIN =================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
