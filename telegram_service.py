import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_mensaje(lat, lon, device_id, timestamp, sat):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Telegram Config Error: Faltan variables de entorno")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Formatear el mensaje con emojis para la presentación
    mensaje = (
        f"🛰 **NUEVA UBICACIÓN DETECTADA**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🆔 **ID:** `{device_id}`\n"
        f"📡 **Sats:** {sat}\n"
        f"⏰ **Hora:** {timestamp} UTC\n"
        f"📍 **Coordenadas:** `{lat}, {lon}`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🗺 [Ver en Google Maps](https://www.google.com/maps?q={lat},{lon})"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        return False
