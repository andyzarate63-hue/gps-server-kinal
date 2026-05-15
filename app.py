from flask import Flask, request, jsonify
from datetime import datetime, timezone
import os
import logging

# Importaciones de tus otros archivos
from telegram_service import enviar_mensaje
from database import (
    init_db,
    insert_location,
    get_last_location
)

# Configuración de logs para ver la actividad en Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# La API KEY debe coincidir con la de tu código de Arduino
API_KEY = os.getenv("API_KEY", "gps123")

# Crear la base de datos si no existe
init_db()

def es_duplicado(device_id, lat, lon):
    """ Evita saturar si el tracker no se ha movido más de 10 metros """
    last = get_last_location(device_id)
    if not last:
        return False
    # Comparación de cercanía (aprox 10m)
    return abs(last[0] - lat) < 0.0001 and abs(last[1] - lon) < 0.0001

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online", "message": "Servidor GPS Activo"}), 200

@app.route("/gps", methods=["POST"])
def gps():
    try:
        # Obtenemos los datos sin importar el header que mande el ESP32
        data = request.get_json(force=True, silent=True) or request.form.to_dict()
        
        # Validación de seguridad básica
        if not data or str(data.get("key")) != API_KEY:
            logger.warning("Intento de conexión no autorizado")
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        device_id = str(data["id"]).strip()
        lat = round(float(data["lat"]), 6)
        lon = round(float(data["lon"]), 6)
        sat = int(data.get("sat", 0))
        
        # Generar timestamp actual
        now = datetime.now(timezone.utc)
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        # Filtro de movimiento
        if es_duplicado(device_id, lat, lon):
            logger.info(f"📍 {device_id} estático. No se envía a Telegram.")
            return jsonify({"status": "ignored", "reason": "static"}), 200

        # Guardar en SQLite
        insert_location(device_id, lat, lon, sat, timestamp)
        
        # Enviar notificación
        envio_ok = enviar_mensaje(lat, lon, device_id, timestamp, sat)
        
        logger.info(f"✅ Ubicación recibida de {device_id}")
        return jsonify({"status": "success", "telegram": envio_ok}), 200

    except Exception as e:
        logger.error(f"❌ Error en el servidor: {str(e)}")
        return jsonify({"status": "error", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
