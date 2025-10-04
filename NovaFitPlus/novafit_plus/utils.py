import os, json, datetime as _dt

def load_config(path: str = "config.json") -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"config.json not found in {os.getcwd()}")
    with open(path, "r", encoding="utf-8") as f:
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
