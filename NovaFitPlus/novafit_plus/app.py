from .utils import load_config, today_iso, clamp, print_box, ascii_bar
from .db import init_db, upsert_user, get_user, upsert_activity, insert_weather, tail, migrate_schema, sleep_on_date, InvalidTableError
from .db import daily_water_total, weather_on_date, reset_to_default, get_data_summary
from . import weather as wz
from .profile import bmi, bmr_mifflin, maintenance_calories
from .hydration import add_intake, hydration_progress, daily_water_goal_ml
from .analysis import kpis, best_running_days, hydration_adherence, sleep_stats, health_score
from .export import export_json, export_excel
from typing import Optional
import datetime as _dt


def _default_profile(name: str):
    return (None, name, 30, "M", 166, 66, "light", "", "")


def onboarding(db, default_name="Kevin"):
    print_box("Onboarding — Profile")
    cfg = load_config()
    existing = get_user(db, default_name)
    if existing:
        _, ex_name, ex_age, ex_sex, ex_h, ex_w, ex_al, ex_city, ex_country = existing
    else:
        _, ex_name, ex_age, ex_sex, ex_h, ex_w, ex_al, ex_city, ex_country = _default_profile(default_name)
    name_default = ex_name or default_name
    name = input(f"Name (default {name_default}): ").strip() or name_default
    age = int(input(f"Age [{ex_age}]: ").strip() or ex_age)
    sex = input(f"Sex (M/F/Other) [{ex_sex}]: ").strip() or ex_sex
    height_cm = float(input(f"Height cm [{ex_h}]: ").strip() or ex_h)
    weight_kg = float(input(f"Weight kg [{ex_w}]: ").strip() or ex_w)
    activity_level_default = (ex_al or "light").lower()
    activity_level = (
        input(
            f"Activity level (sedentary/light/moderate/active) [{activity_level_default}]: "
        )
        .strip()
        .lower()
        or activity_level_default
    )
    city_default = ex_city or cfg.get("default_city", "")
    country_default = ex_country or cfg.get("default_country", "")
    city = input(f"City (default {city_default or 'n/a'}): ").strip() or city_default
    country = input(f"Country (default {country_default or 'n/a'}): ").strip() or country_default
    upsert_user(db, name, age, sex, height_cm, weight_kg, activity_level, city, country)
    val, cat = bmi(weight_kg, height_cm)
    bmr = bmr_mifflin(age, sex, height_cm, weight_kg)
    maint = maintenance_calories(bmr, activity_level)
    print(f"Saved. BMI: {val} ({cat}) | BMR: {bmr} kcal | Maintenance: {maint} kcal")
    return name

def _ensure_iso_date(value: str) -> str:
    try:
        return _dt.date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValueError("Invalid date. Please use YYYY-MM-DD.") from exc


def _resolve_date_input(date_input: Optional[str], prompt: str) -> str:
    default = today_iso()
    if date_input is not None:
        return _ensure_iso_date(date_input.strip() or default)
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        candidate = raw or default
        try:
            return _ensure_iso_date(candidate)
        except ValueError:
            print("Invalid date. Please use YYYY-MM-DD.")


def log_activity(db, user_name, date_input: Optional[str] = None):
    date = _resolve_date_input(date_input, "Date (YYYY-MM-DD)")
    print_box(f"Log Activity ({date})")
    steps = int(input("Steps: ") or 0)
    calories = int(input("Calories: ") or 0)
    mood = clamp(int(input("Mood (1-5): ") or 3), 1, 5)
    notes = input("Notes: ").strip()
    sleep = float(input("Sleep hours: ") or 0)
    upsert_activity(db, user_name, date, steps, calories, mood, notes, sleep)
    print(f"Activity saved for {date}.")


def log_water(db, user_name, date_input: Optional[str] = None):
    date = _resolve_date_input(date_input, "Date (YYYY-MM-DD)")
    print_box(f"Log Water Intake ({date})")
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
    print(f"Added {ml} ml ({src}) for {date}. Total for {date}: {total} ml.")

def dashboard(db, user_name):
    print_box("Daily Dashboard")
    u = get_user(db, user_name) or _default_profile(user_name)
    _, name, age, sex, h, w, al, city, country = u
    b, cat = bmi(w, h)
    bmr = bmr_mifflin(age, sex, h, w)
    maint = maintenance_calories(bmr, al)
    prog = hydration_progress(db, user_name, today_iso(), w)
    bar = ascii_bar(prog["total_ml"], prog["goal_ml"])
    print(f"User: {name} | Age: {age} | Sex: {sex} | Activity: {al}")
    if city or country:
        loc_parts = [part for part in (city, country) if part]
        print(f"Location: {', '.join(loc_parts)}")
    else:
        print("Location: not set")
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
                fetch_city = (city or '').strip() or cfg['default_city']
                fetch_country = (country or '').strip() or cfg['default_country']
                lat, lon, cname = wz.geocode_city(fetch_city, fetch_country)
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

def fetch_weather(db, cfg, user_name):
    print_box("Weather Fetch")
    profile = get_user(db, user_name)
    city_default = (profile[7] if profile else "") or cfg["default_city"]
    country_default = (profile[8] if profile else "") or cfg["default_country"]
    city = input(f"City (default {city_default}): ").strip() or city_default
    country = input(f"Country (default {country_default}): ").strip() or country_default
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
    u = get_user(db, user_name) or _default_profile(user_name)
    _, _, _, _, h, w, al, _, _ = u
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

def do_reset(db):
    """Handle application reset with confirmation"""
    print_box("Reset Application")
    
    # Show current data summary
    summary = get_data_summary(db)
    print("Current data in database:")
    print(f"  Users: {summary['users']}")
    print(f"  Activities: {summary['activities']}")
    print(f"  Weather records: {summary['weather']}")
    print(f"  Water intake records: {summary['water_intake']}")
    print()
    
    if summary['users'] == 0 and summary['activities'] == 0 and summary['weather'] == 0 and summary['water_intake'] == 0:
        print("✅ Database is already empty.")
        return
    
    print("⚠️  WARNING: This will PERMANENTLY DELETE all data!")
    print("   - All user profiles")
    print("   - All activity logs")
    print("   - All weather data")
    print("   - All water intake records")
    print()
    
    confirmation = input("Type 'RESET' to confirm deletion (or anything else to cancel): ").strip()
    
    if confirmation == "RESET":
        print("\n🗑️  Deleting all data...")
        reset_to_default(db)
        print("✅ Application reset completed!")
        print("💡 You can now start fresh with a new profile.")
        
        # Clear cache files if they exist
        import os
        cache_files = ["weather_cache.json", "gamification_Kevin.json"]
        for cache_file in cache_files:
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                    print(f"🧹 Cleared cache file: {cache_file}")
                except:
                    pass
        
    else:
        print("❌ Reset cancelled. No data was deleted.")

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
        print("2) Log activity")
        print("3) Log water intake")
        print("4) Daily dashboard")
        print("5) Fetch & save weather")
        print("6) Analytics")
        print("7) Export JSON + Excel")
        print("8) Seed demo data")
        print("9) Tail last rows")
        print("R) Reset application (DELETE ALL DATA)")
        print("0) Exit")
        op = input("\nChoose: ").strip().upper()

        if op == "1":
            user_name = onboarding(db, default_name=user_name)
        elif op == "2":
            log_activity(db, user_name)
        elif op == "3":
            log_water(db, user_name)
        elif op == "4":
            dashboard(db, user_name)
        elif op == "5":
            fetch_weather(db, cfg, user_name)
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
            tables = ("users", "activities", "weather", "water_intake")
            for tbl in tables:
                print_box(f"{tbl} (last 5)")
                try:
                    print(tail(db, tbl, 5))
                except InvalidTableError as err:
                    print(f"Table error: {err}")
        elif op == "R":
            do_reset(db)
            # After reset, user needs to create profile again
            user_name = onboarding(db, default_name=default)
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
