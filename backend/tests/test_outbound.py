import os
import sqlite3
import sys

# Ensure backend root directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from src.db import (
    get_farmer_info,
    init_db,
    is_opted_out,
    log_call,
    set_opt_out_status,
)
from src.telephony.outbound.dial import normalize_sip_destination


def test_normalize_sip_destination():
    assert normalize_sip_destination("sonali721") == "sip:sonali721@sip.linphone.org"
    assert (
        normalize_sip_destination("sip:sonali721@sip.linphone.org")
        == "sip:sonali721@sip.linphone.org"
    )
    assert (
        normalize_sip_destination("farmer@customdomain.com")
        == "sip:farmer@customdomain.com"
    )
    assert (
        normalize_sip_destination(" sip:sonali721@sip.linphone.org ")
        == "sip:sonali721@sip.linphone.org"
    )


def test_database_operations(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_krishimitra.db")
    monkeypatch.setattr("src.db.DB_PATH", test_db)

    init_db()
    info = get_farmer_info("sip:sonali721@sip.linphone.org")
    assert info is not None
    assert info["name"] == "Sonali"
    assert info["crop"] == "Soybean"
    assert info["threshold_price"] == 5000.0
    assert info["current_price"] == 5200.0
    assert info["opted_out"] == 0

    assert not is_opted_out("sip:sonali721@sip.linphone.org")

    set_opt_out_status("sip:sonali721@sip.linphone.org", True)
    assert is_opted_out("sip:sonali721@sip.linphone.org")

    log_call(
        "test-room-123",
        "sip:sonali721@sip.linphone.org",
        "answered",
        "Test call completed",
    )

    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status, notes FROM call_logs WHERE room_name = ?", ("test-room-123",)
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "answered"
    assert row[1] == "Test call completed"
