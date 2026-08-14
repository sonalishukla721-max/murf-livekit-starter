import datetime
import os
import re
import sqlite3

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "krishimitra.db"
)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def sanitize_sensitive_data(text: str) -> str:
    if not text:
        return ""
    # Mask card numbers (13 to 19 digits)
    text = re.sub(
        r"\b(?:\d[ -]*?){13,19}\b",
        lambda m: "**** **** **** " + re.sub(r"\D", "", m.group(0))[-4:],
        text,
    )
    # Mask 10-12 digit bank account numbers
    text = re.sub(
        r"\b\d{10,12}\b",
        lambda m: "********" + m.group(0)[-4:],
        text,
    )
    # Mask explicitly labeled credentials/OTPs/PINs/CVVs
    text = re.sub(
        r"(?i)\b(otp|pin|cvv|password)\s*[:=]\s*\S+",
        r"\1: [REDACTED]",
        text,
    )
    return text


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

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS escalations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference_id TEXT UNIQUE NOT NULL,
            user_name TEXT NOT NULL,
            issue_type TEXT NOT NULL,
            summary TEXT NOT NULL,
            urgency TEXT NOT NULL,
            language TEXT DEFAULT 'English',
            preferred_followup TEXT DEFAULT 'Phone',
            status TEXT NOT NULL DEFAULT 'open',
            agent_checks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_id TEXT DEFAULT 'anonymous',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration INTEGER DEFAULT 0,
            channel TEXT DEFAULT 'browser',
            outcome TEXT DEFAULT 'FAILED',
            failure_type TEXT,
            success INTEGER DEFAULT 0,
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

    # Seed default demo escalations if table is empty
    cursor.execute("SELECT COUNT(*) FROM escalations")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            """
            INSERT INTO escalations (reference_id, user_name, issue_type, summary, urgency, language, preferred_followup, status, agent_checks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "FIN-2026-4821",
                "Rahul Sharma",
                "Possible Fraud",
                "Caller reports an unrecognized transaction and says they did not authorize it. The issue requires human review.",
                "high",
                "Hindi",
                "Phone",
                "open",
                "FinSahayak identified the report as a possible unauthorized transaction and did not make unsupported claims about the account.",
            ),
        )
        cursor.execute(
            """
            INSERT INTO escalations (reference_id, user_name, issue_type, summary, urgency, language, preferred_followup, status, agent_checks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "FIN-2026-3094",
                "Priya Patel",
                "Complex Financial Case",
                "Customer requested a manual review of complex loan restructuring options beyond standard eligibility formulas.",
                "medium",
                "English",
                "Email",
                "in_progress",
                "FinSahayak gathered case summary and requested customer consent before escalating to senior advisor.",
            ),
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


def save_escalation(
    user_name: str,
    issue_type: str,
    summary: str,
    urgency: str,
    language: str = "English",
    preferred_followup: str = "Phone",
    reference_id: str = "",
    agent_checks: str = "",
) -> dict:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    if not reference_id:
        import random

        year = datetime.datetime.now().year
        rand_digits = random.randint(1000, 9999)
        reference_id = f"FIN-{year}-{rand_digits}"

    sanitized_summary = sanitize_sensitive_data(summary)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if not agent_checks:
        if "fraud" in issue_type.lower():
            agent_checks = "FinSahayak identified the report as a possible unauthorized transaction and did not make unsupported claims about the account."
        else:
            agent_checks = "FinSahayak gathered case summary and verified user permission before creating human support request."

    cursor.execute(
        """
        INSERT INTO escalations (reference_id, user_name, issue_type, summary, urgency, language, preferred_followup, status, agent_checks, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'open', ?, ?, ?)
        """,
        (
            reference_id,
            user_name or "Valued Customer",
            issue_type or "General Financial Issue",
            sanitized_summary,
            urgency or "medium",
            language or "English",
            preferred_followup or "Phone",
            agent_checks,
            now,
            now,
        ),
    )
    conn.commit()
    escalation_id = cursor.lastrowid
    conn.close()

    return {
        "id": escalation_id,
        "reference_id": reference_id,
        "user_name": user_name,
        "issue_type": issue_type,
        "summary": sanitized_summary,
        "urgency": urgency,
        "language": language,
        "preferred_followup": preferred_followup,
        "status": "open",
        "created_at": now,
    }


def get_escalations(
    status: str | None = None,
    urgency: str | None = None,
    issue_type: str | None = None,
    search: str | None = None,
) -> list[dict]:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM escalations WHERE 1=1"
    params = []

    if status and status.lower() != "all":
        query += " AND status = ?"
        params.append(status.lower())

    if urgency and urgency.lower() != "all":
        query += " AND urgency = ?"
        params.append(urgency.lower())

    if issue_type and issue_type.lower() != "all":
        query += " AND issue_type LIKE ?"
        params.append(f"%{issue_type}%")

    if search:
        query += " AND (reference_id LIKE ? OR user_name LIKE ? OR summary LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_escalation_by_id_or_ref(id_or_ref: str) -> dict | None:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    if id_or_ref.isdigit():
        cursor.execute("SELECT * FROM escalations WHERE id = ?", (int(id_or_ref),))
    else:
        cursor.execute("SELECT * FROM escalations WHERE reference_id = ?", (id_or_ref,))

    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_escalation_status(escalation_id: int | str, new_status: str) -> bool:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if str(escalation_id).isdigit():
        cursor.execute(
            "UPDATE escalations SET status = ?, updated_at = ? WHERE id = ?",
            (new_status.lower(), now, int(escalation_id)),
        )
    else:
        cursor.execute(
            "UPDATE escalations SET status = ?, updated_at = ? WHERE reference_id = ?",
            (new_status.lower(), now, str(escalation_id)),
        )

    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def get_escalation_stats() -> dict:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT status, COUNT(*) as cnt FROM escalations GROUP BY status")
    status_counts = {row["status"]: row["cnt"] for row in cursor.fetchall()}

    cursor.execute(
        "SELECT COUNT(*) as cnt FROM escalations WHERE urgency IN ('high', 'emergency') AND status != 'resolved'"
    )
    high_priority_cnt = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM escalations")
    total_cnt = cursor.fetchone()["cnt"]

    conn.close()
    return {
        "open": status_counts.get("open", 0),
        "in_progress": status_counts.get("in_progress", 0),
        "resolved": status_counts.get("resolved", 0),
        "high_priority": high_priority_cnt,
        "total": total_cnt,
    }


def save_call_record(
    session_id: str,
    user_id: str = "anonymous",
    started_at: str | None = None,
    ended_at: str | None = None,
    duration: int = 0,
    channel: str = "browser",
    outcome: str = "FAILED",
    failure_type: str | None = None,
    success: int = 0,
) -> dict:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if not started_at:
        started_at = now
    if not ended_at:
        ended_at = now

    success_val = 1 if (success or outcome == "SUCCESS") else 0
    outcome_val = "SUCCESS" if success_val == 1 else "FAILED"
    failure_val = None if success_val == 1 else (failure_type or "TASK_INCOMPLETE")

    cursor.execute(
        """
        INSERT OR REPLACE INTO calls (session_id, user_id, started_at, ended_at, duration, channel, outcome, failure_type, success, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            user_id,
            started_at,
            ended_at,
            duration,
            channel,
            outcome_val,
            failure_val,
            success_val,
            now,
        ),
    )
    conn.commit()
    call_id = cursor.lastrowid
    conn.close()

    return {
        "id": call_id,
        "session_id": session_id,
        "user_id": user_id,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration": duration,
        "channel": channel,
        "outcome": outcome_val,
        "failure_type": failure_val,
        "success": success_val,
    }


def get_call_analytics() -> dict:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as cnt FROM calls")
    total_calls = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM calls WHERE success = 1")
    successful_calls = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM calls WHERE success = 0")
    failed_calls = cursor.fetchone()["cnt"]

    cursor.execute(
        "SELECT id, session_id, user_id, started_at, ended_at, duration, channel, outcome, failure_type, success, created_at FROM calls ORDER BY created_at DESC LIMIT 20"
    )
    recent_calls = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "total_calls": total_calls,
        "successful_calls": successful_calls,
        "failed_calls": failed_calls,
        "recent_calls": recent_calls,
    }


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
