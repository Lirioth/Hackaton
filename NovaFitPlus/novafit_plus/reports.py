
import os
import datetime as dt
from typing import Dict, Iterable

from matplotlib.figure import Figure

from .db import get_conn
from .hydration import daily_water_goal_ml

EXPORT_DIR = "exports/charts"


def ensure_dir(path: str) -> str:
    """Ensure output directories exist and return the resolved path."""
    os.makedirs(path, exist_ok=True)
    return path


def _dates_range(days: int) -> Iterable[str]:
    """Generate ISO dates for the requested lookback window."""
    start = dt.date.today() - dt.timedelta(days=days - 1)
    for i in range(days):
        yield (start + dt.timedelta(days=i)).isoformat()


def hydration_trend_figure(db_path: str, user_name: str, weight_kg: float, days: int = 14) -> Figure:
    """Build the hydration adherence trend figure for the selected user."""
    dates, percentages = [], []
    with get_conn(db_path) as conn:
        cur = conn.cursor()
        for date in _dates_range(days):
            goal = daily_water_goal_ml(weight_kg, date, db_path, user_name)
            cur.execute(
                """
                SELECT COALESCE(SUM(ml), 0)
                FROM water_intake wi
                JOIN users u ON wi.user_id = u.id
                WHERE u.name = ? AND wi.date = ?
                """,
                (user_name, date),
            )
            total = int(cur.fetchone()[0] or 0)
            pct = 0 if goal <= 0 else round(total * 100 / goal, 1)
            dates.append(date)
            percentages.append(pct)

    fig = Figure(figsize=(6.4, 3.6))
    ax = fig.add_subplot(111)
    if dates:
        ax.plot(dates, percentages, marker="o", color="#2563eb")
        ax.set_ylim(0, max(110, max(percentages) + 10))
    else:
        ax.text(0.5, 0.5, "No hydration data", ha="center", va="center")
    ax.set_title("Hydration adherence (%)")
    ax.set_ylabel("Percent of goal")
    ax.set_xlabel("Date")
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_ha("right")
    fig.tight_layout()
    return fig


def steps_vs_sleep_figure(db_path: str, user_name: str, days: int = 14) -> Figure:
    """Build the steps vs sleep scatter plot."""
    cutoff = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    steps, sleep = [], []
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
            (user_name, cutoff),
        )
        for st, sl in cur.fetchall():
            if st is not None and sl is not None:
                steps.append(st)
                sleep.append(sl)

    fig = Figure(figsize=(6.4, 3.6))
    ax = fig.add_subplot(111)
    if steps:
        ax.scatter(steps, sleep, color="#10b981", alpha=0.8)
    else:
        ax.text(0.5, 0.5, "No activity data", ha="center", va="center")
    ax.set_title("Steps vs Sleep")
    ax.set_xlabel("Steps")
    ax.set_ylabel("Sleep hours")
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    return fig


def sleep_vs_goal_figure(db_path: str, user_name: str, goal_hours: float = 8.0, days: int = 14) -> Figure:
    """Create a bar chart comparing nightly sleep with a fixed goal."""
    dates, sleeps = [], []
    with get_conn(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.date, a.sleep_hours
            FROM activities a
            JOIN users u ON a.user_id = u.id
            WHERE u.name = ? AND a.date >= ?
            ORDER BY a.date ASC
            """,
            (user_name, (dt.date.today() - dt.timedelta(days=days - 1)).isoformat()),
        )
        for date, hours in cur.fetchall():
            dates.append(date)
            sleeps.append(hours or 0)

    fig = Figure(figsize=(6.4, 3.6))
    ax = fig.add_subplot(111)
    if dates:
        ax.bar(dates, sleeps, color="#8b5cf6")
        ax.axhline(goal_hours, color="#f59e0b", linestyle="--", label=f"Goal: {goal_hours}h")
        ax.legend()
    else:
        ax.text(0.5, 0.5, "No sleep logs", ha="center", va="center")
    ax.set_title("Sleep vs Goal")
    ax.set_ylabel("Sleep hours")
    ax.set_xlabel("Date")
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_ha("right")
    fig.tight_layout()
    return fig


def save_report_figures(figures: Dict[str, Figure], outdir: str = EXPORT_DIR) -> Dict[str, str]:
    """Persist report figures to disk and return their file paths."""
    ensure_dir(outdir)
    saved: Dict[str, str] = {}
    for name, figure in figures.items():
        path = os.path.join(outdir, f"{name}.png")
        figure.savefig(path, dpi=150, bbox_inches="tight")
        saved[name] = path
    return saved


def chart_hydration(db_path: str, user_name: str, weight_kg: float, days: int = 14, outdir: str = EXPORT_DIR) -> str:
    """Backward compatible helper returning the saved hydration trend path."""
    figure = hydration_trend_figure(db_path, user_name, weight_kg, days)
    paths = save_report_figures({"hydration_pct": figure}, outdir)
    return paths["hydration_pct"]


def chart_steps_vs_sleep(db_path: str, user_name: str, days: int = 14, outdir: str = EXPORT_DIR) -> str:
    """Backward compatible helper returning the saved steps vs sleep path."""
    figure = steps_vs_sleep_figure(db_path, user_name, days)
    paths = save_report_figures({"steps_vs_sleep": figure}, outdir)
    return paths["steps_vs_sleep"]
