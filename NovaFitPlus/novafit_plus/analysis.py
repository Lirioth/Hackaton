import datetime as dt, statistics
from .db import get_conn, steps_on_date, daily_water_total, weather_on_date
from .hydration import daily_water_goal_ml

def kpis(db_path: str, user_name: str, days: int = 14):
    start = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    with get_conn(db_path) as c:
        cur = c.cursor()
        cur.execute(
            '''SELECT date, steps, calories, mood, sleep_hours
               FROM activities a JOIN users u ON a.user_id=u.id
               WHERE u.name=? AND date >= ?
               ORDER BY date ASC''', (user_name, start)
        )
        rows = cur.fetchall()

    if not rows:
        return {"message": "No activities found in the requested range."}

    steps = [r[1] for r in rows if r[1] is not None]
    calories = [r[2] for r in rows if r[2] is not None]
    moods = [r[3] for r in rows if r[3] is not None]
    sleeps = [r[4] for r in rows if r[4] is not None]

    def movavg(vals, w=7):
        out = []
        for i in range(len(vals)):
            j = max(0, i - w + 1)
            out.append(sum(vals[j:i+1]) / (i - j + 1))
        return out

    return {
        "days_count": len(rows),
        "steps_avg": round(statistics.mean(steps), 2) if steps else None,
        "calories_avg": round(statistics.mean(calories), 2) if calories else None,
        "mood_avg": round(statistics.mean(moods), 2) if moods else None,
        "sleep_avg": round(statistics.mean(sleeps), 2) if sleeps else None,
        "steps_movavg_7d_last": round(movavg(steps)[-1], 2) if steps else None
    }

def best_running_days(db_path: str, days: int = 14):
    start = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    with get_conn(db_path) as c:
        cur = c.cursor()
        cur.execute(
            '''SELECT w.date, w.temp_max, w.humidity, w.wind_speed, w.condition
               FROM weather w
               WHERE w.date >= ?
               ORDER BY w.date ASC''', (start,)
        )
        rows = cur.fetchall()

    scored = []
    for d, tmax, hum, wind, cond in rows:
        score = 0
        if tmax is not None:
            score += max(0, 10 - abs(22 - tmax))
        if hum is not None:
            score += 5 if hum < 70 else 1
        if wind is not None:
            score += 5 if wind < 20 else 1
        scored.append((d, cond, round(score, 2)))

    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:5]

def hydration_adherence(db_path: str, user_name: str, weight_kg: float, days: int = 7):
    start = (dt.date.today() - dt.timedelta(days=days-1))
    report = []
    for i in range(days):
        d = (start + dt.timedelta(days=i)).isoformat()
        goal = daily_water_goal_ml(weight_kg, d, db_path, user_name)
        actual = daily_water_total(db_path, user_name, d)
        pct = 0 if goal <= 0 else round(actual * 100 / goal, 1)
        weather = weather_on_date(db_path, d)
        tmax = weather[0] if weather else None
        report.append({"date": d, "goal_ml": goal, "total_ml": actual, "pct": pct, "tmax": tmax})
    return report

def sleep_stats(db_path: str, user_name: str, days: int = 7):
    start = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    with get_conn(db_path) as c:
        cur = c.cursor()
        cur.execute(
            '''SELECT a.sleep_hours
               FROM activities a JOIN users u ON a.user_id=u.id
               WHERE u.name=? AND a.date >= ?
               ORDER BY a.date ASC''', (user_name, start)
        )
        rows = cur.fetchall()
    sleeps = [r[0] for r in rows if r[0] is not None]
    avg_h = round(statistics.mean(sleeps), 2) if sleeps else 0.0
    pct = round((avg_h / 8.0) * 100, 1) if avg_h > 0 else 0.0
    return {"avg_hours": avg_h, "percent_vs_8h": pct, "days": days, "samples": len(sleeps)}

def hydration_avg_pct(db_path: str, user_name: str, weight_kg: float, days: int = 7):
    rep = hydration_adherence(db_path, user_name, weight_kg, days=days)
    if not rep:
        return 0.0
    pcts = [row["pct"] for row in rep if row["pct"] is not None]
    return round(statistics.mean(pcts), 1) if pcts else 0.0

def health_score(db_path: str, user_name: str, weight_kg: float, height_cm: float, days: int = 7):
    k = kpis(db_path, user_name, days)
    steps_avg = k.get("steps_avg") or 0
    steps_score = min(100, (steps_avg / 10000.0) * 100)
    hyd_pct = hydration_avg_pct(db_path, user_name, weight_kg, days)
    hyd_score = min(100, max(0, hyd_pct))
    ss = sleep_stats(db_path, user_name, days)
    sleep_score = min(100, ss["percent_vs_8h"])
    mood_avg = k.get("mood_avg") or 0
    mood_score = max(0, min(100, (mood_avg - 1) / 4 * 100)) if mood_avg else 0
    try:
        h_m = max(0.5, height_cm/100.0)
        bmi_val = weight_kg/(h_m*h_m)
    except Exception:
        bmi_val = 0
    bmi_pen = 0
    if bmi_val and (bmi_val < 18.5 or bmi_val >= 30):
        bmi_pen = 8
    elif bmi_val >= 25:
        bmi_pen = 4
    score = 0.30*steps_score + 0.30*hyd_score + 0.30*sleep_score + 0.10*mood_score
    score = max(0, min(100, round(score - bmi_pen, 1)))
    return {
        "score": score,
        "components": {
            "steps_score": round(steps_score,1),
            "hydration_score": round(hyd_score,1),
            "sleep_score": round(sleep_score,1),
            "mood_score": round(mood_score,1),
            "bmi_penalty": bmi_pen
        },
        "basis_days": days
    }
