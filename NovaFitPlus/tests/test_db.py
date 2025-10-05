import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from novafit_plus.db import get_conn


def test_get_conn_allows_plain_filenames(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    db_file = "plain_name.db"
    with get_conn(db_file) as conn:
        conn.execute("SELECT 1")
    assert os.path.isfile(db_file)
