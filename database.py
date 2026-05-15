import sqlite3

DB_NAME = "gps_data.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT, lat REAL, lon REAL, sat INTEGER, timestamp TEXT
            )
        """)

def insert_location(device_id, lat, lon, sat, timestamp):
    with get_connection() as conn:
        conn.execute("INSERT INTO locations (device_id, lat, lon, sat, timestamp) VALUES (?, ?, ?, ?, ?)",
                     (device_id, lat, lon, sat, timestamp))

def get_last_location(device_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT lat, lon FROM locations WHERE device_id = ? ORDER BY id DESC LIMIT 1", (device_id,))
        return c.fetchone()
