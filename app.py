from flask import Flask, request, jsonify
from datetime import datetime, timezone
import os
import logging

# Importamos las funciones de tus otros archivos
from telegram_service import enviar_mensaje
from database import (
    init_db,
    insert_location,
    get_history,
    get_last_location,
    get_last_seen
)

# Configuración de logs para ver errores en el dashboard de Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Variables de entorno
# El segundo valor es el que se usa si no configuras nada en el panel de Render
API_KEY = os.getenv("API_KEY", "gps123") 

# Inicializamos la base de datos al arrancar
init_db()

def validar_datos(data):
    if not data:
        return False, "Cuerpo de mensaje vacío"
    
    required = ["id", "lat", "lon", "key"]
    for field in required:
        if field not in data:
            return False, f"Falta el campo: {field}"

    if data.get("key") != API_KEY:
        return False, "API KEY no coincide"

    try:
        lat = float(data["lat"])
        lon = float(data["lon"])
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return False, "Coordenadas fuera de rango global"
    except (ValueError, TypeError):
        return False, "Formato de coordenadas inválido"

    return True, ""

def es_duplicado(device_id, lat, lon):
    last = get_last_location(device_id)
    if not last:
        return False
    
    last_lat, last_lon, _, _ = last
    # Filtro de movimiento (aprox 8-10 metros)
    if abs(last_lat - lat) < 0.00008 and abs(last_lon - lon) < 0.00008:
        return True
    return False

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ready", "message": "Servidor GPS Activo"}), 200

@app.route("/gps", methods=["POST"])
def gps():
    try:
        data = request.get_json()
        ok, error_msg = validar_datos(data)

        if not ok:
            logger.warning(f"Validación fallida: {error_msg}")
            return jsonify({"status": "error", "message": error_msg}), 400

        device_id = str(data["id"]).strip()
        lat = round(float(data["lat"]), 6)
        lon = round(float(data["lon"]), 6)
        sat = int(data.get("sat", 0))
        # Usamos hora UTC para evitar confusiones de zona horaria
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        if es_duplicado(device_id, lat, lon):
            return jsonify({"status": "ignored", "reason": "static_position"}), 200

        # 1. Guardar en SQLite
        insert_location(device_id, lat, lon, sat, timestamp)
        
        # 2. Notificar a Telegram
        enviar_mensaje(lat, lon, device_id, timestamp, sat)

        logger.info(f"📍 Ubicación recibida de {device_id}")
        return jsonify({"status": "success", "device": device_id}), 200

    except Exception as e:
        logger.error(f"Error crítico: {str(e)}")
        return jsonify({"status": "server_error", "details": str(e)}), 500

if __name__ == "__main__":
    # CAMBIO: Usamos el puerto 10000 por defecto, que es el preferido por Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
