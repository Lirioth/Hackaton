
import os, datetime as dt
import matplotlib
matplotlib.use('Agg')  # headless
import matplotlib.pyplot as plt
from .db import get_conn
from .hydration import daily_water_goal_ml
from .analysis import kpis

def ensure_dir(p): os.makedirs(p, exist_ok=True); return p

def chart_hydration(db_path: str, user_name: str, weight_kg: float, days: int = 14, outdir: str = "exports/charts") -> str:
    ensure_dir(outdir)
    start = dt.date.today() - dt.timedelta(days=days-1)
    dates, goals, totals, pcts = [], [], [], []
    with get_conn(db_path) as c:
        cur = c.cursor()
        for i in range(days):
            d = (start + dt.timedelta(days=i)).isoformat()
            goal = daily_water_goal_ml(weight_kg, d, db_path, user_name)
            cur.execute("SELECT COALESCE(SUM(ml),0) FROM water_intake wi JOIN users u ON wi.user_id=u.id WHERE u.name=? AND wi.date=?", (user_name, d))
            tot = int(cur.fetchone()[0] or 0)
            pct = 0 if goal <= 0 else round(tot*100/goal, 1)
            dates.append(d); goals.append(goal); totals.append(tot); pcts.append(pct)
    # One plot: pct over time
    plt.figure()
    plt.plot(dates, pcts, marker='o')
    plt.xticks(rotation=45, ha='right')
    plt.title("Hydration adherence (%)")
    plt.tight_layout()
    path = os.path.join(outdir, "hydration_pct.png")
    plt.savefig(path); plt.close()
    return path

def chart_steps_vs_sleep(db_path: str, user_name: str, days: int = 14, outdir: str = "exports/charts") -> str:
    ensure_dir(outdir)
    start = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    xs, ys = [], []
    with get_conn(db_path) as c:
        cur = c.cursor()
        cur.execute('''SELECT a.steps, a.sleep_hours
                       FROM activities a JOIN users u ON a.user_id=u.id
                       WHERE u.name=? AND a.date >= ?
                       ORDER BY a.date ASC''', (user_name, start))
        for st, sl in cur.fetchall():
            if st is not None and sl is not None:
                xs.append(st); ys.append(sl)
    # One scatter plot
    plt.figure()
    plt.scatter(xs, ys)
    plt.xlabel("Steps"); plt.ylabel("Sleep hours")
    plt.title("Steps vs Sleep")
    plt.tight_layout()
    path = os.path.join(outdir, "steps_vs_sleep.png")
    plt.savefig(path); plt.close()
    return path
