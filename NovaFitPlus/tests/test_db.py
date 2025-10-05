import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from novafit_plus.db import get_conn, init_db, migrate_schema, upsert_user, get_user
from novafit_plus.utils import load_config


def test_get_conn_allows_plain_filenames(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    db_file = "plain_name.db"
    with get_conn(db_file) as conn:
        conn.execute("SELECT 1")
    assert os.path.isfile(db_file)


def test_migrate_schema_adds_location_columns(tmp_path):
    db_path = tmp_path / "legacy.db"
    init_db(str(db_path))
    with get_conn(str(db_path)) as conn:
        cur = conn.cursor()
        cur.execute("DROP TABLE users")
        cur.execute(
            '''CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                age INTEGER,
                sex TEXT,
                height_cm REAL,
                weight_kg REAL,
                activity_level TEXT,
                created_at TEXT
            )'''
        )
        cur.execute(
            "INSERT INTO users(name, age, sex, height_cm, weight_kg, activity_level, created_at) VALUES (?,?,?,?,?,?,DATE('now'))",
            ("Alice", 28, "F", 165.0, 60.0, "light"),
        )
    migrate_schema(str(db_path))
    cfg = load_config()
    with get_conn(str(db_path)) as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(users)")
        cols = {row[1] for row in cur.fetchall()}
        assert "city" in cols and "country" in cols
        cur.execute("SELECT city, country FROM users WHERE name=?", ("Alice",))
        city, country = cur.fetchone()
        assert city == cfg.get("default_city")
        assert country == cfg.get("default_country")


def test_upsert_user_round_trip_with_location(tmp_path):
    db_path = tmp_path / "profile.db"
    init_db(str(db_path))
    migrate_schema(str(db_path))
    upsert_user(
        str(db_path),
        "Bob",
        32,
        "M",
        178.0,
        80.0,
        "moderate",
        "Lisbon",
        "Portugal",
    )
    row = get_user(str(db_path), "Bob")
    assert row[7] == "Lisbon"
    assert row[8] == "Portugal"
