from flask import Flask, request, jsonify
from datetime import datetime, timezone
import os
import logging

from telegram_service import enviar_mensaje
from database import (
    init_db,
    insert_location,
    get_history,
    get_last_location,
    get_last_seen
)

# Configuración de logs para ver errores en tiempo real en Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Variable de seguridad (Debe ser igual en Arduino y Render)
API_KEY = os.getenv("API_KEY", "gps123")

# Inicializar la base de datos al arrancar
init_db()

def validar_datos(data):
    """ Valida que el JSON tenga todo lo necesario """
    if not data:
        return False, "Cuerpo de mensaje vacío o no es JSON"
    
    # IMPORTANTE: Aquí verificamos 'id', que es lo que manda el ESP32
    required = ["id", "lat", "lon", "key"]
    for field in required:
        if field not in data:
            return False, f"Falta el campo obligatorio: {field}"

    # Verificación de la API KEY
    if str(data.get("key")) != API_KEY:
        return False, "API KEY no autorizada"

    # Verificación de formato numérico
    try:
        lat = float(data["lat"])
        lon = float(data["lon"])
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return False, "Coordenadas fuera de rango geográfico"
    except (ValueError, TypeError):
        return False, "Latitud o Longitud no son números válidos"

    return True, ""

def es_duplicado(device_id, lat, lon):
    """ Evita guardar puntos si el dispositivo no se ha movido (aprox 8 metros) """
    last = get_last_location(device_id)
    if not last:
        return False
    
    last_lat, last_lon, _, _ = last
    if abs(last_lat - lat) < 0.00008 and abs(last_lon - lon) < 0.00008:
        return True
    return False

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "Servidor de Rastreo GPS funcionando correctamente"
    }), 200

@app.route("/gps", methods=["POST"])
def gps():
    try:
        # Intentar obtener el JSON
        data = request.get_json(silent=True)
        
        # 1. Validar datos
        ok, error_msg = validar_datos(data)
        if not ok:
            logger.warning(f"Petición rechazada: {error_msg}")
            return jsonify({"status": "error", "message": error_msg}), 400

        # 2. Extraer información limpia
        device_id = str(data["id"]).strip()
        lat = round(float(data["lat"]), 6)
        lon = round(float(data["lon"]), 6)
        sat = int(data.get("sat", 0))
        
        # Timestamp en formato legible para humanos
        now = datetime.now(timezone.utc)
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        # 3. Verificar si está quieto para no saturar Telegram
        if es_duplicado(device_id, lat, lon):
            logger.info(f"📍 {device_id} está estático. Omitiendo duplicado.")
            return jsonify({"status": "ignored", "reason": "static_position"}), 200

        # 4. Guardar en SQLite
        insert_location(device_id, lat, lon, sat, timestamp)
        
        # 5. Enviar a Telegram
        # Pasamos los datos a la función de telegram_service
        envio_ok = enviar_mensaje(lat, lon, device_id, timestamp, sat)
        
        if envio_ok:
            logger.info(f"✅ Datos de {device_id} procesados y enviados a Telegram.")
        else:
            logger.error(f"⚠️ Datos guardados pero falló el envío a Telegram.")

        return jsonify({
            "status": "success",
            "message": "Ubicación procesada",
            "device": device_id
        }), 200

    except Exception as e:
        logger.error(f"❌ Error interno del servidor: {str(e)}")
        return jsonify({"status": "server_error", "error": str(e)}), 500

if __name__ == "__main__":
    # Render asigna un puerto automáticamente
    port = int(os.environ.get("PORT", 80))
    app.run(host="0.0.0.0", port=port)
