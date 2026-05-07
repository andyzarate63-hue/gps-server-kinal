import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def enviar_mensaje(lat, lon, device_id, timestamp):

    if not BOT_TOKEN or not CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    mensaje = (
        f"📍 GPS TRACKER\n\n"
        f"🆔 ID: {device_id}\n"
        f"🛰 Satélites: GPS ACTIVE\n"
        f"🕒 Hora UTC: {timestamp}\n\n"
        f"🌍 Latitud: {lat}\n"
        f"🌍 Longitud: {lon}\n\n"
        f"📌 Google Maps:\n"
        f"https://maps.google.com/?q={lat},{lon}"
    )

    try:

        response = requests.post(
            url,
            json={
                "chat_id": CHAT_ID,
                "text": mensaje
            },
            timeout=10
        )

        return response.status_code == 200

    except Exception as e:

        print(f"Telegram Error: {e}")

        return False
