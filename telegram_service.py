import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_mensaje(lat, lon):
    if not BOT_TOKEN or not CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    mensaje = f"📍 GPS\nLat: {lat}\nLon: {lon}\nhttps://maps.google.com/?q={lat},{lon}"

    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except:
        return False
