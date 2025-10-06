
import os
import datetime as dt
from typing import Dict, List

import matplotlib

matplotlib.use('Agg')  # headless
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from .db import get_conn
from .hydration import daily_water_goal_ml


def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def _date_labels(start: dt.date, days: int) -> List[str]:
    """Generate ISO date labels for the requested window. 📅"""

    return [(start + dt.timedelta(days=offset)).isoformat() for offset in range(days)]


def chart_hydration(db_path: str, user_name: str, weight_kg: float, days: int = 14) -> Figure:
    """Create a hydration adherence figure ready for embedding. 💧"""

    start = dt.date.today() - dt.timedelta(days=days - 1)
    dates = _date_labels(start, days)
    percentages: List[float] = []
    with get_conn(db_path) as conn:
        cur = conn.cursor()
        for label in dates:
            goal = daily_water_goal_ml(weight_kg, label, db_path, user_name)
            cur.execute(
                """
                SELECT COALESCE(SUM(ml), 0)
                FROM water_intake wi
                JOIN users u ON wi.user_id = u.id
                WHERE u.name = ? AND wi.date = ?
                """,
                (user_name, label),
            )
            total = int(cur.fetchone()[0] or 0)
            pct = 0.0 if goal <= 0 else round(total * 100 / goal, 1)
            percentages.append(pct)

    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.plot(dates, percentages, marker="o", color="#3b82f6")
    ax.set_title("Hydration adherence (%)")
    ax.set_ylabel("Percent of goal")
    ax.set_ylim(0, max(100, max(percentages or [0]) + 10))
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig


def chart_steps_vs_sleep(db_path: str, user_name: str, days: int = 14) -> Figure:
    """Build a scatter chart comparing steps and sleep duration. 💤"""

    start = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    steps: List[int] = []
    sleep_hours: List[float] = []
    with get_conn(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.steps, a.sleep_hours
            FROM activities a
            JOIN users u ON a.user_id = u.id
            WHERE u.name = ? AND a.date >= ?
            ORDER BY a.date ASC
            """,
            (user_name, start),
        )
        for steps_val, sleep_val in cur.fetchall():
            if steps_val is not None and sleep_val is not None:
                steps.append(int(steps_val))
                sleep_hours.append(float(sleep_val))

    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    if steps:
        ax.scatter(steps, sleep_hours, color="#10b981", alpha=0.85)
    else:
        ax.text(0.5, 0.5, "No paired entries", ha="center", va="center", transform=ax.transAxes)
    ax.set_xlabel("Steps")
    ax.set_ylabel("Sleep hours")
    ax.set_title("Steps vs Sleep")
    fig.tight_layout()
    return fig


def chart_sleep_vs_goal(db_path: str, user_name: str, days: int = 14, goal_hours: float = 8.0) -> Figure:
    """Plot sleep duration against a consistent goal line. 🌙"""

    start = dt.date.today() - dt.timedelta(days=days - 1)
    dates = _date_labels(start, days)
    actual_sleep: List[float] = []
    with get_conn(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.date, a.sleep_hours
            FROM activities a
            JOIN users u ON a.user_id = u.id
            WHERE u.name = ? AND a.date BETWEEN ? AND ?
            ORDER BY a.date ASC
            """,
            (user_name, dates[0], dates[-1]),
        )
        sleep_map = {row_date: float(hours) for row_date, hours in cur.fetchall() if hours is not None}
    for label in dates:
        actual_sleep.append(sleep_map.get(label, 0.0))

    goal_series = [goal_hours for _ in dates]
    upper = max(goal_series + actual_sleep or [goal_hours])

    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.plot(dates, actual_sleep, marker="o", label="Actual", color="#8b5cf6")
    ax.plot(dates, goal_series, linestyle="--", label=f"Goal ({goal_hours}h)", color="#6366f1")
    if any(actual_sleep):
        ax.fill_between(dates, actual_sleep, goal_series, color="#c4b5fd", alpha=0.3)
    ax.set_ylim(0, max(upper + 1, goal_hours + 1))
    ax.set_ylabel("Hours")
    ax.set_title("Sleep vs Goal")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    fig.tight_layout()
    return fig


def save_report_figures(figures: Dict[str, Figure], outdir: str = "exports/charts", dpi: int = 120) -> Dict[str, str]:
    """Persist report figures to disk for sharing. 💾"""

    ensure_dir(outdir)
    saved_paths: Dict[str, str] = {}
    for name, figure in figures.items():
        filename = f"{name}.png"
        path = os.path.join(outdir, filename)
        figure.savefig(path, dpi=dpi, bbox_inches="tight")
        saved_paths[name] = path
    return saved_paths
