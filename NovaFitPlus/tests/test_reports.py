import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from novafit_plus.db import add_water_intake, init_db, upsert_user
from novafit_plus.reports import chart_hydration


def test_chart_hydration_creates_both_charts(tmp_path):
    db_path = tmp_path / "hydration.db"
    init_db(str(db_path))
    upsert_user(str(db_path), "TestUser", 30, "F", 165, 60, "light")
    today = dt.date.today()
    for offset in range(3):
        date = (today - dt.timedelta(days=offset)).isoformat()
        add_water_intake(str(db_path), "TestUser", date, 600 + offset * 50, "glass")

    pct_path, comparison_path = chart_hydration(str(db_path), "TestUser", 60, days=3, outdir=str(tmp_path))

    assert Path(pct_path).is_file()
    assert Path(comparison_path).is_file()
