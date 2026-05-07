import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def enviar_mensaje(lat, lon, device_id, timestamp):

    if not BOT_TOKEN or not CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    mensaje = (
        f"📍 GPS TRACKER\n"
        f"ID: {device_id}\n"
        f"Hora: {timestamp}\n"
        f"Lat: {lat}\n"
        f"Lon: {lon}\n"
        f"Mapa: https://maps.google.com/?q={lat},{lon}"
    )

    try:
        r = requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": mensaje
        }, timeout=10)

        return r.status_code == 200

    except:
        return False
