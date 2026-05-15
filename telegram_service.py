import requests
import os

def enviar_mensaje(lat, lon, device_id, timestamp, sat):
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    
    if not token or not chat_id:
        return False

    # Este formato de URL es el que mejor acepta Telegram para mostrar el mapa
    maps_url = f"https://www.google.com/maps?q={lat},{lon}"
    
    mensaje = (
        f"🛰 **UBICACIÓN DETECTADA**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🆔 **ID:** `{device_id}`\n"
        f"📡 **Sats:** {sat}\n"
        f"⏰ **Hora:** {timestamp} UTC\n"
        f"📍 **Coordenadas:** `{lat}, {lon}`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🗺 [VER EN GOOGLE MAPS]({maps_url})"
    )

    payload = {
        "chat_id": chat_id,
        "text": mensaje,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }

    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json=payload, timeout=10)
        return r.status_code == 200
    except:
        return False
