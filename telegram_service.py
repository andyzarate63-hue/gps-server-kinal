import requests
import os

# Estas variables se configuran en el panel de Environment de Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_mensaje(lat, lon, device_id, timestamp, sat):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Error: Configura BOT_TOKEN y CHAT_ID en Render")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Estructura del mensaje para Telegram
    # Corregido: El enlace de Google Maps ahora es estándar y funcional
    mensaje = (
        f"🛰 **RASTREO GPS ACTIVO**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🆔 **ID:** `{device_id}`\n"
        f"📡 **Satélites:** {sat}\n"
        f"⏰ **Hora:** {timestamp} UTC\n"
        f"📍 **Lat/Lon:** `{lat}, {lon}`\n"
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
        # Enviamos la petición a los servidores de Telegram
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"❌ Error de Telegram: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error crítico en el servicio de Telegram: {e}")
        return False
