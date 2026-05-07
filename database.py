from datetime import datetime

def get_last_location(device_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT lat, lon, sat, timestamp
        FROM locations
        WHERE device_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (device_id,))

    row = c.fetchone()
    conn.close()

    return row


def get_last_seen(device_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT timestamp
        FROM locations
        WHERE device_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (device_id,))

    row = c.fetchone()
    conn.close()

    return row[0] if row else None
