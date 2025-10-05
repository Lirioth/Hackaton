import os, json, datetime as _dt
from pathlib import Path
from importlib import resources
from typing import Optional, Union


_CONFIG_RESOURCE = "config.json"
_ENV_CONFIG = "NOVAFIT_CONFIG"


PathLike = Union[str, os.PathLike]


def _try_path(candidate: Optional[PathLike]) -> Optional[dict]:
    if not candidate:
        return None
    path = Path(candidate).expanduser()
    if path.is_file():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return None


def load_config(path: Optional[PathLike] = None) -> dict:
    cfg = _try_path(path)
    if cfg is not None:
        return cfg

    cfg = _try_path(os.environ.get(_ENV_CONFIG))
    if cfg is not None:
        return cfg

    package_files = resources.files(__package__)
    resource_path = package_files / _CONFIG_RESOURCE
    if not resource_path.is_file():
        raise FileNotFoundError("Bundled configuration missing from package")
    with resource_path.open("r", encoding="utf-8") as f:
        return json.load(f)

def today_iso():
    return _dt.date.today().isoformat()

def clamp(n, lo, hi):
    return max(lo, min(n, hi))

def print_box(title: str):
    line = "═" * (len(title) + 2)
    print(f"╔{line}╗")
    print(f"║ {title} ║")
    print(f"╚{line}╝")

def ascii_bar(current: float, goal: float, width: int = 24) -> str:
    if goal <= 0:
        goal = 1
    ratio = max(0.0, min(1.0, current / goal))
    done = int(ratio * width)
    return f"[{'#'*done}{'.'*(width-done)}] {int(ratio*100)}%"
