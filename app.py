from flask import Flask, request, jsonify
from datetime import datetime
import os
from telegram_service import enviar_mensaje

app = Flask(__name__)

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ================= LOG =================
def log(msg):
    print(f"[{datetime.now()}] {msg}")

# ================= VALIDACIÓN =================
def validar_datos(data):
    if not data:
        return False, "No se recibió JSON"

    if not isinstance(data, dict):
        return False, "Formato inválido"

    if "lat" not in data or "lon" not in data:
        return False, "Faltan campos obligatorios"

    try:
        lat = float(data["lat"])
        lon = float(data["lon"])
    except:
        return False, "Lat/Lon deben ser numéricos"

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return False, "Coordenadas fuera de rango"

    return True, ""

# ================= RUTA PRINCIPAL =================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "GPS Tracker API",
        "telegram_config": bool(BOT_TOKEN and CHAT_ID)
    }), 200

# ================= RUTA GPS =================
@app.route("/gps", methods=["POST"])
def gps():
    try:
        data = request.get_json()

        valido, error = validar_datos(data)
        if not valido:
            log(f"Error validación: {error}")
            return jsonify({"error": error}), 400

        lat = float(data["lat"])
        lon = float(data["lon"])

        log(f"GPS recibido: {lat}, {lon}")

        # Enviar a Telegram SOLO si está configurado
        if BOT_TOKEN and CHAT_ID:
            enviado = enviar_mensaje(lat, lon)
            if not enviado:
                log("Fallo al enviar a Telegram")
                return jsonify({"error": "Error Telegram"}), 500
        else:
            log("Telegram no configurado")

        return jsonify({
            "status": "ok",
            "lat": lat,
            "lon": lon
        }), 200

    except Exception as e:
        log(f"Error interno: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# ================= MAIN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
