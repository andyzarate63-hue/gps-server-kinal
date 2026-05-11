import sqlite3

DB_NAME = "gps_data.db"

# =========================================================
# CONEXIÓN
# =========================================================
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    # El modo WAL mejora el rendimiento para escrituras frecuentes
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

# =========================================================
# INICIALIZAR BASE DE DATOS
# =========================================================
def init_db():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                sat INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL
            )
        """)
        # Índice para que las consultas de historial sean rápidas
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_device_id
            ON locations(device_id)
        """)
        conn.commit()

# =========================================================
# INSERTAR NUEVA UBICACIÓN
# =========================================================
def insert_location(device_id, lat, lon, sat, timestamp):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO locations (
                device_id,
                lat,
                lon,
                sat,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            device_id,
            lat,
            lon,
            sat,
            timestamp
        ))
        conn.commit()

# =========================================================
# OBTENER HISTORIAL (La función que faltaba)
# =========================================================
def get_history(device_id, limit=50):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT
                lat,
                lon,
                sat,
                timestamp
            FROM locations
            WHERE device_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (
            device_id,
            limit
        ))
        return c.fetchall()

# =========================================================
# OBTENER ÚLTIMA UBICACIÓN
# =========================================================
def get_last_location(device_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT
                lat,
                lon,
                sat,
                timestamp
            FROM locations
            WHERE device_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (device_id,))
        return c.fetchone()

# =========================================================
# OBTENER ÚLTIMA VEZ VISTO (TIMESTAMP)
# =========================================================
def get_last_seen(device_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT timestamp
            FROM locations
            WHERE device_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (device_id,))
        row = c.fetchone()
        return row[0] if row else None
