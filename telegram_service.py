import requests

# CREDENCIALES VERIFICADAS
BOT_TOKEN = "8777412272:AAE5JJFj39yL6QtWPx-d3mBHvBn1mD6DFhM"
CHAT_ID = "8420372209"

def enviar_mensaje(lat, lon, device_id, timestamp, sat):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Creamos un mensaje extremadamente simple sin simbolos raros
    # El enlace se pone al final para que Telegram lo reconozca facil
    texto = (
        "UBICACION DETECTADA\n"
        f"ID: {device_id}\n"
        f"Satelites: {sat}\n"
        f"Coordenadas: {lat}, {lon}\n"
        f"Mapa: https://www.google.com/maps?q={lat},{lon}"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": texto
    }

    try:
        # Enviamos la peticion
        response = requests.post(url, json=payload, timeout=10)
        
        # Esto es para que tú lo veas en los logs de Render
        print(f"Respuesta de Telegram: {response.status_code}")
        print(f"Detalle: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error de conexion: {e}")
        return False
