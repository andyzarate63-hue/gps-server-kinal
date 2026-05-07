import requests
import os
from datetime import datetime
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def construir_mensaje(lat, lon, device_id, timestamp):
    maps = f"https://maps.google.com/?q={lat},{lon}"

    return (
        f"📍 GPS TRACKER\n"
        f"━━━━━━━━━━━━━━━\n"
        f"ID: {device_id}\n"
        f"Hora: {timestamp}\n"
        f"Lat: {lat}\n"
        f"Lon: {lon}\n"
        f"Mapa: {maps}\n"
        f"━━━━━━━━━━━━━━━"
    )


def enviar_mensaje(lat, lon, device_id, timestamp, intentos=3):

    if not BOT_TOKEN or not CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    mensaje = construir_mensaje(lat, lon, device_id, timestamp)

    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje
    }

    for i in range(intentos):
        try:
            r = requests.post(url, json=payload, timeout=10)

            if r.status_code == 200:
                return True

        except Exception as e:
            time.sleep(1)

    return False
