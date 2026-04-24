from flask import Flask, request, jsonify
from datetime import datetime
from telegram_service import enviar_mensaje

app = Flask(__name__)

# ================= LOG =================
def log(msg):
    print(f"[{datetime.now()}] {msg}")

# ================= VALIDACIÓN =================
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

        if not enviar_mensaje(lat, lon):
            log("Error enviando a Telegram")
            return jsonify({"error": "Fallo Telegram"}), 500

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        log(f"Error interno: {str(e)}")
        return jsonify({"error": "Error interno"}), 500


# ================= MAIN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
