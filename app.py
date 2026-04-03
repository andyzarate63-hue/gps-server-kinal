from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Estos se configuran en Render para que nadie te robe el Bot
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

@app.route('/gps', methods=['POST'])
def recibir_gps():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON"}), 400
    
    # Formateo del mensaje con link a Google Maps
    mensaje = (
        f"📍 <b>GPS - ESP32 Kinal</b>\n"
        f"Lat: <code>{data.get('lat')}</code>\n"
        f"Lon: <code>{data.get('lon')}</code>\n"
        f"Alt: <code>{data.get('alt')} m</code>\n"
        f"Vel: <code>{data.get('vel')} km/h</code>\n"
        f"Sat: <code>{data.get('sat')}</code>\n"
        f"🔗 <a href='http://www.google.com/maps/place/{data.get('lat')},{data.get('lon')}'>Ver en Mapa</a>"
    )
    
    payload = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "HTML"}
    try:
        requests.post(TELEGRAM_URL, json=payload, timeout=10)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
