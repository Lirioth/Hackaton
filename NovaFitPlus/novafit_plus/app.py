from .utils import load_config, today_iso, clamp, print_box, ascii_bar
from .db import init_db, upsert_user, get_user, upsert_activity, insert_weather, tail, migrate_schema, sleep_on_date
from .db import add_water_intake, daily_water_total, weather_on_date
from . import weather as wz
from .profile import bmi, bmr_mifflin, maintenance_calories
from .hydration import add_intake, hydration_progress, daily_water_goal_ml
from .analysis import kpis, best_running_days, hydration_adherence, sleep_stats, health_score
from .export import export_json, export_excel
from typing import Optional

def onboarding(db, default_name="Kevin"):
    print_box("Onboarding — Profile")
    name = input(f"Name (default {default_name}): ").strip() or default_name
    age = int(input("Age: ") or 30)
    sex = input("Sex (M/F/Other): ").strip() or "M"
    height_cm = float(input("Height cm: ") or 166)
    weight_kg = float(input("Weight kg: ") or 66)
    activity_level = input("Activity level (sedentary/light/moderate/active) [light]: ").strip().lower() or "light"
    upsert_user(db, name, age, sex, height_cm, weight_kg, activity_level)
    val, cat = bmi(weight_kg, height_cm)
    bmr = bmr_mifflin(age, sex, height_cm, weight_kg)
    maint = maintenance_calories(bmr, activity_level)
    print(f"Saved. BMI: {val} ({cat}) | BMR: {bmr} kcal | Maintenance: {maint} kcal")
    return name

def log_activity(db, user_name):
    print_box("Log Activity (today)")
    date = today_iso()
    steps = int(input("Steps: ") or 0)
    calories = int(input("Calories: ") or 0)
    mood = clamp(int(input("Mood (1-5): ") or 3), 1, 5)
    notes = input("Notes: ").strip()
    sleep = float(input("Sleep hours: ") or 0)
    upsert_activity(db, user_name, date, steps, calories, mood, notes, sleep)
    print("Activity saved.")

def log_water(db, user_name):
    print_box("Log Water Intake")
    date = today_iso()
    print("Quick picks: [1]=250ml glass, [2]=500ml bottle, [3]=750ml big bottle, [4]=custom")
    ch = input("Choose: ").strip() or "1"
    if ch == "1":
        ml, src = 250, "glass"
    elif ch == "2":
        ml, src = 500, "bottle"
    elif ch == "3":
        ml, src = 750, "thermos"
    else:
        ml = int(input("Enter ml: ") or 250)
        src = input("Source (glass/bottle/thermos/other): ").strip() or "other"
    add_intake(db, user_name, date, ml, src)
    total = daily_water_total(db, user_name, date)
    print(f"Added {ml} ml ({src}). Today total: {total} ml.")

def dashboard(db, user_name):
    print_box("Daily Dashboard")
    u = get_user(db, user_name) or (None, user_name, 30, "M", 166, 66, "light")
    _, name, age, sex, h, w, al = u
    b, cat = bmi(w, h)
    bmr = bmr_mifflin(age, sex, h, w)
    maint = maintenance_calories(bmr, al)
    prog = hydration_progress(db, user_name, today_iso(), w)
    bar = ascii_bar(prog["total_ml"], prog["goal_ml"])
    print(f"User: {name} | Age: {age} | Sex: {sex} | Activity: {al}")
    print(f"Height: {h} cm | Weight: {w} kg | BMI: {b} ({cat})")
    print(f"BMR: {bmr} kcal | Maintenance: {maint} kcal")
    print(f"Hydration: {prog['total_ml']}/{prog['goal_ml']} ml {bar} (remaining {prog['remaining_ml']} ml)")
    sleep = sleep_on_date(db, user_name, today_iso())
    print(f"Sleep today: {sleep} h")
    w7 = sleep_stats(db, user_name, days=7)
    w30 = sleep_stats(db, user_name, days=30)
    print(f"Weekly sleep vs 8h: {w7['percent_vs_8h']}% | Monthly: {w30['percent_vs_8h']}%")
    hs = health_score(db, user_name, w, h, days=7)
    print(f"Health Score (7d): {hs['score']} / 100  -> components: {hs['components']}")
    wrow = weather_on_date(db, today_iso())
    if wrow:
        tmax, tmin, hum, wind, cond, city = wrow
        print(f"Today's weather [{city}]: max {tmax}°C, min {tmin}°C, humidity {hum}%, wind {wind} km/h, {cond}")
    else:
        ans = input("Today's weather not found. Fetch now? [Y/n] ").strip().lower() or 'y'
        if ans == 'y':
            cfg = load_config()
            try:
                lat, lon, cname = wz.geocode_city(cfg['default_city'], cfg['default_country'])
                data = wz.fetch_daily_forecast(lat, lon, days=1)
                daily = data.get('daily', {})
                for i, d in enumerate(daily.get('time', [])):
                    tmax = daily.get('temperature_2m_max', [None]*len(daily['time']))[i]
                    tmin = daily.get('temperature_2m_min', [None]*len(daily['time']))[i]
                    hum = daily.get('relative_humidity_2m_mean', [None]*len(daily['time']))[i]
                    wind = daily.get('windspeed_10m_max', [None]*len(daily['time']))[i]
                    code = daily.get('weathercode', [None]*len(daily['time']))[i]
                    cond = wz.code_to_text(code) if code is not None else None
                    insert_weather(db, d, cname, lat, lon, tmax, tmin, int(hum) if hum is not None else None, wind, cond)
                wrow2 = weather_on_date(db, today_iso())
                if wrow2:
                    tmax, tmin, hum, wind, cond, city = wrow2
                    print(f"Today's weather [{city}]: max {tmax}°C, min {tmin}°C, humidity {hum}%, wind {wind} km/h, {cond}")
            except Exception as e:
                print(f"Weather fetch failed: {e}")
        else:
            print("Skipping weather fetch.")

def fetch_weather(db, cfg):
    print_box("Weather Fetch")
    city = input(f"City (default {cfg['default_city']}): ").strip() or cfg["default_city"]
    country = input(f"Country (default {cfg['default_country']}): ").strip() or cfg["default_country"]
    days = int(input("Days (1-7): ") or 1)
    days = max(1, min(days, 7))
    lat, lon, cname = wz.geocode_city(city, country)
    data = wz.fetch_daily_forecast(lat, lon, days=days)
    daily = data.get("daily", {})
    for i, d in enumerate(daily.get("time", [])):
        tmax = daily.get("temperature_2m_max", [None]*len(daily["time"]))[i]
        tmin = daily.get("temperature_2m_min", [None]*len(daily["time"]))[i]
        hum = daily.get("relative_humidity_2m_mean", [None]*len(daily["time"]))[i]
        wind = daily.get("windspeed_10m_max", [None]*len(daily["time"]))[i]
        code = daily.get("weathercode", [None]*len(daily["time"]))[i]
        cond = wz.code_to_text(code) if code is not None else None
        insert_weather(db, d, cname, lat, lon, tmax, tmin, int(hum) if hum is not None else None, wind, cond)
    print(f"Weather saved for {cname} ({days} day(s)).")

def do_analytics(db, user_name):
    print_box("Analytics")
    days = int(input("Analyze last N days (default 14): ") or 14)
    print_box("Activity KPIs")
    print(kpis(db, user_name, days))
    print_box("Best running days (heuristic)")
    for d, cond, score in best_running_days(db, days):
        print(f"{d} — {cond} — Score: {score}")
    print_box("Hydration adherence (last 7 days)")
    u = get_user(db, user_name) or (None, user_name, 30, "M", 166, 66, "light")
    _, name, age, sex, h, w, al = u
    rep = hydration_adherence(db, user_name, w, days=7)
    for row in rep:
        print(row)
    print_box("Health Score")
    hs = health_score(db, user_name, w, h, days=7)
    print(hs)

def do_export(db, cfg, user_name):
    out_json = export_json(db, cfg["export_dir"], user_name, days=14)
    out_xlsx = export_excel(db, cfg["export_dir"], user_name, days=14)
    print(f"Export ready: {out_json} | {out_xlsx}")

def menu(config_path: Optional[str] = None):
    cfg = load_config(config_path)
    db = cfg["db_path"]
    init_db(db)
    migrate_schema(db)

    print_box("NovaFit Plus CLI")
    default = "Kevin"
    u = get_user(db, default)
    user_name = default
    if not u:
        user_name = onboarding(db, default_name=default)
    else:
        ans = input(f"Use profile '{default}'? [Y/n] ").strip().lower() or "y"
        if ans != "y":
            user_name = onboarding(db, default_name=default)

    while True:
        print_box("Menu")
        print("1) Setup/Update profile")
        print("2) Log TODAY activity")
        print("3) Log water intake")
        print("4) Daily dashboard")
        print("5) Fetch & save weather")
        print("6) Analytics")
        print("7) Export JSON + Excel")
        print("8) Seed demo data")
        print("9) Tail last rows")
        print("0) Exit")
        op = input("\nChoose: ").strip()

        if op == "1":
            user_name = onboarding(db, default_name=user_name)
        elif op == "2":
            log_activity(db, user_name)
        elif op == "3":
            log_water(db, user_name)
        elif op == "4":
            dashboard(db, user_name)
        elif op == "5":
            fetch_weather(db, cfg)
        elif op == "6":
            do_analytics(db, user_name)
        elif op == "7":
            do_export(db, cfg, user_name)
        elif op == "8":
            from .seed import seed_user, seed_faker
            seed_user(db, name=user_name)
            days = int(input("Seed how many days back (default 21): ") or 21)
            seed_faker(db, user_name, days)
            print(f"Seed completed ({days} days).")
        elif op == "9":
            print_box("users (last 5)")
            print(tail(db, "users", 5))
            print_box("activities (last 5)")
            print(tail(db, "activities", 5))
            print_box("weather (last 5)")
            print(tail(db, "weather", 5))
            print_box("water_intake (last 5)")
            print(tail(db, "water_intake", 5))
        elif op == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid option.")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="NovaFit Plus CLI")
    parser.add_argument("--menu", action="store_true", help="Open interactive menu (default)")
    parser.add_argument("--gui", action="store_true", help="Launch Tkinter GUI")
    args = parser.parse_args()
    if args.gui:
        from . import ui_tk
        ui_tk.main()
    else:
        menu()

if __name__ == "__main__":
    main()
