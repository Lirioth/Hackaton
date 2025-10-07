import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from novafit_plus.db import init_db, get_conn, daily_water_total
from novafit_plus.hydration import add_intake
from novafit_plus.db import upsert_activity


def test_custom_date_entries_are_persisted(tmp_path):
    db_file = tmp_path / "custom_dates.db"
    init_db(str(db_file))
    db_path = str(db_file)
    user_name = "TestUser"
    custom_date = "2024-02-29"
    upsert_activity(db_path, user_name, custom_date, 1200, 500, 4, "Test notes", 7.5)
    with get_conn(db_path) as conn:
        row = conn.execute("SELECT date FROM activities WHERE date=?", (custom_date,)).fetchone()
    assert row is not None
    assert row[0] == custom_date
    add_intake(db_path, user_name, custom_date, 300, "unit-test")
    with get_conn(db_path) as conn:
        water_row = conn.execute("SELECT date, ml FROM water_intake WHERE date=?", (custom_date,)).fetchone()
    assert water_row is not None
    assert water_row[0] == custom_date
    assert water_row[1] == 300
    total = daily_water_total(db_path, user_name, custom_date)
    assert total == 300
