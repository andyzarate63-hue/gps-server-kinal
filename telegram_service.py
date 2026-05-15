import requests
import os

def enviar_mensaje(lat, lon, device_id, timestamp, sat):
    # Se obtienen de las variables de entorno de Render
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    
    if not token or not chat_id:
        print("⚠️ Error: BOT_TOKEN o CHAT_ID no configurados en Render")
        return False

    # URL universal corregida para Google Maps
    maps_url = f"https://www.google.com/maps?q={lat},{lon}"
    
    mensaje = (
        f"🛰 **RASTREO GPS ACTIVO**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🆔 **ID:** `{device_id}`\n"
        f"📡 **Satélites:** {sat}\n"
        f"⏰ **Hora:** {timestamp} UTC\n"
        f"📍 **Posición:** `{lat}, {lon}`\n"
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
        response = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error enviando a Telegram: {e}")
        return False
