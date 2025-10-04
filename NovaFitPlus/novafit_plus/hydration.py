from .db import daily_water_total, steps_on_date, weather_on_date, add_water_intake
from .utils import clamp

def daily_water_goal_ml(weight_kg: float, date: str, db_path: str, user_name: str) -> int:
    base = weight_kg * 35.0
    steps = steps_on_date(db_path, user_name, date)
    if steps >= 12000:
        base += 500
    elif steps >= 8000:
        base += 250
    w = weather_on_date(db_path, date)
    if w:
        tmax, tmin, hum, wind, cond, city = w
        if tmax is not None:
            if tmax > 32:
                base += 1000
            elif tmax > 28:
                base += 500
        if hum is not None and hum >= 70:
            base += 250
    return int(clamp(base, 1500, 6000))

def add_intake(db_path: str, user_name: str, date: str, ml: int, source: str):
    ml = max(0, int(ml))
    add_water_intake(db_path, user_name, date, ml, source)

def hydration_progress(db_path: str, user_name: str, date: str, weight_kg: float) -> dict:
    goal = daily_water_goal_ml(weight_kg, date, db_path, user_name)
    total = daily_water_total(db_path, user_name, date)
    return {"goal_ml": goal, "total_ml": total, "remaining_ml": max(0, goal - total)}
