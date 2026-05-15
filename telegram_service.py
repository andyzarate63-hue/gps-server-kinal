import requests

# Tus credenciales verificadas
BOT_TOKEN = "8777412272:AAFPqyY5eeObXoM4DUS18amhuBd-A5ILNms"
CHAT_ID = "8420372209"

def enviar_mensaje(lat, lon, device_id, timestamp, sat):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Enlace directo de Google Maps
    maps_url = f"https://www.google.com/maps?q={lat},{lon}"
    
    # Texto plano y directo
    mensaje = (
        "NUEVA UBICACION GPS\n"
        "-------------------\n"
        f"Dispositivo: {device_id}\n"
        f"Satelites: {sat}\n"
        f"Coordenadas: {lat}, {lon}\n"
        "-------------------\n"
        f"Mapa: {maps_url}"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"Respuesta Telegram: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"Falla de conexion con Telegram: {e}")
        return False
