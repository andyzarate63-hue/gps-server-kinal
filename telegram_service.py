import requests

# TOKEN Y ID REVERIFICADOS
BOT_TOKEN = "8777412272:AAFPqyY5eeObXoM4DUS18amhuBd-A5ILNms"
CHAT_ID = "8420372209"

def enviar_mensaje(lat, lon, device_id, timestamp, sat):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Enlace de Google Maps simplificado
    maps_url = f"https://www.google.com/maps?q={lat},{lon}"
    
    # Mensaje en texto plano (Sin negritas ni símbolos que den error)
    mensaje = (
        "ALERTA GPS KINAL\n"
        "-------------------\n"
        f"ID: {device_id}\n"
        f"Satelites: {sat}\n"
        f"Hora: {timestamp} UTC\n"
        f"Latitud: {lat}\n"
        f"Longitud: {lon}\n"
        "-------------------\n"
        f"VER MAPA: {maps_url}"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        # Esto te dirá en los logs de Render qué pasó exactamente
        print(f"Respuesta Telegram: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error conexion Telegram: {e}")
        return False
