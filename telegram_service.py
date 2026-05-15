import requests

# CREDENCIALES ACTUALIZADAS
BOT_TOKEN = "8777412272:AAFPqyY5eeObXoM4DUS18amhuBd-A5ILNms"
CHAT_ID = "8420372209"

def enviar_mensaje(lat, lon, device_id, timestamp, sat):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Enlace universal
    maps_url = f"https://www.google.com/maps?q={lat},{lon}"
    
    mensaje = (
        "🛰 RASTREO GPS KINAL\n"
        "---------------------------\n"
        f"ID: {device_id}\n"
        f"Satélites: {sat}\n"
        f"Hora: {timestamp} UTC\n"
        f"Posición: {lat}, {lon}\n"
        "---------------------------\n"
        f"MAPA: {maps_url}"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "disable_web_page_preview": False
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except:
        return False
