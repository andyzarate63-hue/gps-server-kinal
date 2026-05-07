import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_mensaje(lat, lon, device_id, timestamp):

    if not BOT_TOKEN or not CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    maps = f"https://maps.google.com/?q={lat},{lon}"

    text = (
        f"📍 TRACKER ACTIVADO\n"
        f"ID: {device_id}\n"
        f"Hora: {timestamp}\n"
        f"Lat: {lat}\n"
        f"Lon: {lon}\n"
        f"Mapa: {maps}"
    )

    try:
        r = requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": text
        }, timeout=10)

        return r.status_code == 200

    except:
        return False
