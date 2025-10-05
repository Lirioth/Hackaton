from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from novafit_plus.db import init_db, get_conn, tail, InvalidTableError


def test_tail_allows_whitelisted_tables(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(str(db_path))
    with get_conn(str(db_path)) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO users(name) VALUES (?)", ("Alice",))
    rows = tail(str(db_path), "users", 5)
    assert rows
    assert rows[0][1] == "Alice"


def test_tail_rejects_disallowed_table(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(str(db_path))
    with pytest.raises(InvalidTableError):
        tail(str(db_path), "not_allowed")
