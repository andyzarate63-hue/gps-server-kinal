import requests
import os

def enviar_mensaje(lat, lon, device_id, timestamp, sat):
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    
    if not token or not chat_id:
        print("⚠️ Faltan variables de entorno para Telegram")
        return False

    # URL universal para mapas (corregida)
    maps_url = f"http://maps.google.com/maps?q={lat},{lon}"
    
    mensaje = (
        f"🛰 **GPS TRACKER: {device_id}**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📡 **Sats:** {sat}\n"
        f"⏰ **Hora:** {timestamp} UTC\n"
        f"📍 **Ubicación:** `{lat}, {lon}`\n"
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
    except Exception as e:
        print(f"Error de conexión con Telegram: {e}")
        return False
