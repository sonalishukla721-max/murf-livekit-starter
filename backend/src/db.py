import datetime
import os
import sqlite3

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "krishimitra.db"
)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_or_sip TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            crop TEXT NOT NULL,
            threshold_price REAL NOT NULL,
            current_price REAL NOT NULL,
            opted_out INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS call_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT NOT NULL,
            sip_destination TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Seed default demo farmer if table is empty
    cursor.execute("SELECT COUNT(*) FROM farmers")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            """
            INSERT INTO farmers (phone_or_sip, name, crop, threshold_price, current_price, opted_out)
            VALUES (?, ?, ?, ?, ?, 0)
            """,
            ("sip:sonali721@sip.linphone.org", "Sonali", "Soybean", 5000.0, 5200.0),
        )

    conn.commit()
    conn.close()


def get_farmer_info(phone_or_sip: str) -> dict | None:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farmers WHERE phone_or_sip = ?", (phone_or_sip,))
    row = cursor.fetchone()

    if not row and "sonali721" in phone_or_sip:
        cursor.execute("SELECT * FROM farmers WHERE phone_or_sip LIKE '%sonali721%'")
        row = cursor.fetchone()

    conn.close()
    if row:
        return dict(row)
    return {
        "phone_or_sip": phone_or_sip,
        "name": "Farmer",
        "crop": "Soybean",
        "threshold_price": 5000.0,
        "current_price": 5200.0,
        "opted_out": 0,
    }


def set_opt_out_status(phone_or_sip: str, opted_out: bool = True) -> bool:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    opt_val = 1 if opted_out else 0
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    cursor.execute(
        "UPDATE farmers SET opted_out = ?, updated_at = ? WHERE phone_or_sip = ?",
        (opt_val, now, phone_or_sip),
    )
    if cursor.rowcount == 0:
        cursor.execute(
            "UPDATE farmers SET opted_out = ?, updated_at = ? WHERE phone_or_sip LIKE ?",
            (opt_val, now, f"%{phone_or_sip}%"),
        )
    if cursor.rowcount == 0:
        cursor.execute(
            """
            INSERT INTO farmers (phone_or_sip, name, crop, threshold_price, current_price, opted_out, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (phone_or_sip, "Farmer", "Soybean", 5000.0, 5200.0, opt_val, now),
        )

    conn.commit()
    conn.close()
    return True


def is_opted_out(phone_or_sip: str) -> bool:
    info = get_farmer_info(phone_or_sip)
    if info:
        return bool(info.get("opted_out", 0))
    return False


def log_call(room_name: str, sip_destination: str, status: str, notes: str = ""):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO call_logs (room_name, sip_destination, status, notes)
        VALUES (?, ?, ?, ?)
        """,
        (room_name, sip_destination, status, notes),
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
