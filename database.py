import sqlite3

DB_NAME = "gps_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            lat REAL,
            lon REAL,
            sat INTEGER,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_location(device_id, lat, lon, sat, timestamp):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        INSERT INTO locations (device_id, lat, lon, sat, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (device_id, lat, lon, sat, timestamp))

    conn.commit()
    conn.close()


def get_history(device_id, limit=50):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT lat, lon, sat, timestamp
        FROM locations
        WHERE device_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (device_id, limit))

    rows = c.fetchall()
    conn.close()

    return rows
