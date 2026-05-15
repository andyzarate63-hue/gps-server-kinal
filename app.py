from flask import Flask, request, jsonify
import os
import logging
from telegram_service import enviar_mensaje
from database import init_db, insert_location

# Configuración de logs para que puedas ver errores en el panel de Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Usamos la API_KEY que tienes configurada en Render, por defecto 'gps123'
API_KEY = os.getenv("API_KEY", "gps123")

# Intentar inicializar la base de datos
try:
    init_db()
except Exception as e:
    logger.error(f"Error al inicializar DB: {e}")

@app.route("/", methods=["GET"])
def home():
    return "Servidor GPS Kinal Operativo", 200

@app.route("/gps", methods=["POST"])
def gps():
    try:
        # Forzamos la lectura del JSON
        data = request.get_json(force=True, silent=True)
        
        if not data or str(data.get("key")) != API_KEY:
            logger.warning("Intento de acceso no autorizado")
            return "Unauthorized", 401

        dev_id = data.get("id", "AndyTracker")
        lat = data.get("lat")
        lon = data.get("lon")
        sat = data.get("sat", 0)
        timestamp = "Ahora" # Simplificado para evitar errores de librería de tiempo

        # Intentar guardar en base de datos de forma segura
        try:
            insert_location(dev_id, lat, lon, sat, timestamp)
        except Exception as db_err:
            logger.error(f"Error de base de datos: {db_err}")

        # Intentar enviar a Telegram de forma segura
        # Aunque Telegram falle, devolveremos 200 para que el LCD no marque Error 500
        try:
            enviar_mensaje(lat, lon, dev_id, timestamp, sat)
        except Exception as tg_err:
            logger.error(f"Error de Telegram: {tg_err}")

        return "OK", 200

    except Exception as e:
        logger.error(f"Falla crítica en el servidor: {e}")
        # Devolvemos 200 incluso en error para que el LCD no se bloquee
        return "Error Procesado", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
