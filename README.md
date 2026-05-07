# 📍 GPS Tracker ESP32 + SIM800L

## 📌 Descripción del proyecto

Este proyecto consiste en un sistema de rastreo GPS en tiempo real utilizando un ESP32 con módulo SIM800L.

El dispositivo envía coordenadas GPS a un servidor en la nube, donde son procesadas, almacenadas en una base de datos SQLite y enviadas automáticamente a Telegram con un enlace directo a Google Maps.

---

## ⚙️ Arquitectura del sistema

ESP32 (GPS)
↓
SIM800L (Internet móvil)
↓
Flask API (Servidor en la nube)
↓
SQLite Database (Historial)
↓
Telegram Bot (Notificaciones en tiempo real)

---

## 🚀 Tecnologías utilizadas

- ESP32  
- Módulo SIM800L  
- Python Flask  
- SQLite  
- Telegram Bot API  
- Render (hosting en la nube)

---

## 📡 Funcionalidades del sistema

- Envío de ubicación GPS en tiempo real  
- Almacenamiento de historial de ubicaciones  
- Eliminación de datos duplicados  
- Estado del dispositivo (online / offline)  
- Envío automático de ubicación a Telegram  
- Consulta de última ubicación  
- Historial completo por dispositivo  

---

## 🔗 Endpoints del servidor

### 📍 Enviar ubicación GPS
**Método:** POST  
**Ruta:** `/gps`  

Envía la ubicación del dispositivo al servidor para ser almacenada y enviada a Telegram.

---

### 📍 Última ubicación registrada
**Método:** GET  
**Ruta:** `/last/<device_id>`  

Devuelve la última ubicación registrada del dispositivo con enlace a Google Maps.

---

### 📍 Historial de ubicaciones
**Método:** GET  
**Ruta:** `/history/<device_id>`  

Devuelve todas las ubicaciones almacenadas del dispositivo.

---

### 📍 Estado del dispositivo
**Método:** GET  
**Ruta:** `/status/<device_id>`  

Indica si el dispositivo está en línea o fuera de línea según su última conexión.
}
