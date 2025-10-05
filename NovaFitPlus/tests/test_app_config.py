import builtins
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from novafit_plus import app


def test_menu_uses_bundled_config_outside_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("NOVAFIT_CONFIG", raising=False)

    responses = iter(["", "", "", "", "", "", "0"])

    def fake_input(_prompt=""):
        try:
            return next(responses)
        except StopIteration:
            return "0"

    monkeypatch.setattr(builtins, "input", fake_input)

    app.menu()

    expected_db = tmp_path / "data" / "novafit_plus.db"
    assert expected_db.exists()
