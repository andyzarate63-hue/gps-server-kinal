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
    if not isinstance(data, dict):
        return False, "JSON inválido"

    if "lat" not in data or "lon" not in data:
        return False, "Faltan campos"

    try:
        lat = float(data["lat"])
        lon = float(data["lon"])
    except:
        return False, "Datos inválidos"

    return True, ""

# ================= RUTAS =================

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "telegram_config": bool(BOT_TOKEN and CHAT_ID)
    })

@app.route("/gps", methods=["POST"])
def gps():
    data = request.get_json()

    valido, error = validar_datos(data)
    if not valido:
        return jsonify({"error": error}), 400

    lat = data["lat"]
    lon = data["lon"]

    log(f"GPS recibido: {lat}, {lon}")

    # 🔥 IMPORTANTE: no romper si falta telegram
    if BOT_TOKEN and CHAT_ID:
        if not enviar_mensaje(lat, lon):
            return jsonify({"error": "Telegram fallo"}), 500
    else:
        log("Telegram no configurado")

    return jsonify({"status": "ok"}), 200


# ================= MAIN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
