import requests
import os

# --- TOKEN ACTUALIZADO ---
BOT_TOKEN = "8777412272:AAFPqyY5eeObXoM4DUS18amhuBd-A5ILNms"
CHAT_ID = "8420372209"

def enviar_mensaje(lat, lon, device_id, timestamp, sat):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # URL Estándar de Google Maps
    google_maps_url = f"https://www.google.com/maps?q={lat},{lon}"
    
    mensaje = (
        f"🛰 **GPS TRACKER: {device_id}**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📡 **Sats:** {sat}\n"
        f"⏰ **Hora:** {timestamp} UTC\n"
        f"📍 **Ubicación:** `{lat}, {lon}`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🗺 [VER EN GOOGLE MAPS]({google_maps_url})"
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
        print(f"Error Telegram: {e}")
        return False
