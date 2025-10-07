import os, sqlite3
from contextlib import contextmanager

@contextmanager
def get_conn(db_path: str):
    dir_name = os.path.dirname(db_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

SCHEMA = [
    '''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        age INTEGER,
        sex TEXT,
        height_cm REAL,
        weight_kg REAL,
        activity_level TEXT,
        city TEXT,
        country TEXT,
        created_at TEXT
    );''',
    '''CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        steps INTEGER,
        calories INTEGER,
        mood INTEGER,
        notes TEXT,
        sleep_hours REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );''',
    '''CREATE UNIQUE INDEX IF NOT EXISTS idx_activities_user_date
        ON activities(user_id, date);''',
    '''CREATE TABLE IF NOT EXISTS weather (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        city TEXT,
        latitude REAL,
        longitude REAL,
        temp_max REAL,
        temp_min REAL,
        humidity INTEGER,
        wind_speed REAL,
        condition TEXT
    );''',
    '''CREATE UNIQUE INDEX IF NOT EXISTS idx_weather_date_city
        ON weather(date, city);''',
    '''CREATE TABLE IF NOT EXISTS water_intake (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        ml INTEGER NOT NULL,
        source TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );'''
]

class InvalidTableError(ValueError):
    pass

_TAIL_SQL = {
    "users": "SELECT * FROM users ORDER BY id DESC LIMIT ?",
    "activities": "SELECT * FROM activities ORDER BY id DESC LIMIT ?",
    "weather": "SELECT * FROM weather ORDER BY id DESC LIMIT ?",
    "water_intake": "SELECT * FROM water_intake ORDER BY id DESC LIMIT ?",
}

def init_db(db_path: str):
    with get_conn(db_path) as c:
        cur = c.cursor()
        for sql in SCHEMA:
            cur.execute(sql)

def migrate_schema(db_path: str):
    with get_conn(db_path) as c:
        cur = c.cursor()
        cur.execute("PRAGMA table_info(activities)")
        cols = [r[1] for r in cur.fetchall()]
        if "sleep_hours" not in cols:
            try:
                cur.execute("ALTER TABLE activities ADD COLUMN sleep_hours REAL")
            except Exception:
                pass
        cur.execute("PRAGMA index_list(activities)")
        indexes = {row[1] for row in cur.fetchall()}
        if "idx_activities_user_date" not in indexes:
            cur.execute(
                """
                DELETE FROM activities
                WHERE id NOT IN (
                    SELECT MIN(id) FROM activities GROUP BY user_id, date
                )
                """
            )
            cur.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_activities_user_date
                    ON activities(user_id, date)
                """
            )

        cur.execute("PRAGMA table_info(users)")
        user_cols = [r[1] for r in cur.fetchall()]
        added_city = False
        added_country = False
        if "city" not in user_cols:
            cur.execute("ALTER TABLE users ADD COLUMN city TEXT")
            added_city = True
        if "country" not in user_cols:
            cur.execute("ALTER TABLE users ADD COLUMN country TEXT")
            added_country = True

        if added_city or added_country or "city" in user_cols or "country" in user_cols:
            from .utils import load_config  # local import to avoid cycle 🤖

            cfg = load_config()
            default_city = cfg.get("default_city", "")
            default_country = cfg.get("default_country", "")
        else:
            default_city = ""
            default_country = ""

        if "city" in user_cols or added_city:
            cur.execute(
                "UPDATE users SET city = ? WHERE city IS NULL OR TRIM(city) = ''",
                (default_city,),
            )
        if "country" in user_cols or added_country:
            cur.execute(
                "UPDATE users SET country = ? WHERE country IS NULL OR TRIM(country) = ''",
                (default_country,),
            )

        cur.execute("PRAGMA index_list(weather)")
        weather_indexes = {row[1] for row in cur.fetchall()}
        if "idx_weather_date_city" not in weather_indexes:
            cur.execute(
                """
                DELETE FROM weather
                WHERE id NOT IN (
                    SELECT MIN(id) FROM weather GROUP BY date, city
                )
                """
            )
            cur.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_weather_date_city
                    ON weather(date, city)
                """
            )

def upsert_user(
    db_path: str,
    name: str,
    age: int,
    sex: str,
    height_cm: float,
    weight_kg: float,
    activity_level: str,
    city: str,
    country: str,
):
    with get_conn(db_path) as c:
        cur = c.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO users(name, age, sex, height_cm, weight_kg, activity_level, city, country, created_at) VALUES (?,?,?,?,?,?,?,?,DATE('now'))",
            (name, age, sex, height_cm, weight_kg, activity_level, city, country),
        )
        cur.execute(
            "UPDATE users SET age=?, sex=?, height_cm=?, weight_kg=?, activity_level=?, city=?, country=? WHERE name=?",
            (age, sex, height_cm, weight_kg, activity_level, city, country, name),
        )

def get_user(db_path: str, name: str):
    with get_conn(db_path) as c:
        cur = c.cursor()
        cur.execute(
            "SELECT id, name, age, sex, height_cm, weight_kg, activity_level, city, country FROM users WHERE name=?",
            (name,),
        )
        return cur.fetchone()

def upsert_activity(db_path: str, user_name: str, date: str, steps: int, calories: int, mood: int, notes: str, sleep_hours: float):
    with get_conn(db_path) as c:
        cur = c.cursor()
        cur.execute("INSERT OR IGNORE INTO users(name) VALUES (?)", (user_name,))
        cur.execute("SELECT id FROM users WHERE name=?", (user_name,))
        user_id = cur.fetchone()[0]
        cur.execute(
            '''INSERT INTO activities(user_id, date, steps, calories, mood, notes, sleep_hours)
               VALUES(?,?,?,?,?,?,?)
               ON CONFLICT(user_id, date) DO UPDATE SET
                   steps=excluded.steps,
                   calories=excluded.calories,
                   mood=excluded.mood,
                   notes=excluded.notes,
                   sleep_hours=excluded.sleep_hours''',
            (user_id, date, steps, calories, mood, notes, sleep_hours)
        )

def insert_weather(db_path: str, date: str, city: str, lat: float, lon: float,
                   tmax: float, tmin: float, humidity: int, wind: float, condition: str):
    with get_conn(db_path) as c:
        cur = c.cursor()
        cur.execute(
            '''INSERT INTO weather(date, city, latitude, longitude, temp_max, temp_min, humidity, wind_speed, condition)
               VALUES (?,?,?,?,?,?,?,?,?)
               ON CONFLICT(date, city) DO UPDATE SET
                   latitude=excluded.latitude,
                   longitude=excluded.longitude,
                   temp_max=excluded.temp_max,
                   temp_min=excluded.temp_min,
                   humidity=excluded.humidity,
                   wind_speed=excluded.wind_speed,
                   condition=excluded.condition''',
            (date, city, lat, lon, tmax, tmin, humidity, wind, condition)
        )

def add_water_intake(db_path: str, user_name: str, date: str, ml: int, source: str):
    with get_conn(db_path) as c:
        cur = c.cursor()
        cur.execute("INSERT OR IGNORE INTO users(name) VALUES (?)", (user_name,))
        cur.execute("SELECT id FROM users WHERE name=?", (user_name,))
        user_id = cur.fetchone()[0]
        cur.execute(
            '''INSERT INTO water_intake(user_id, date, ml, source, created_at)
               VALUES (?,?,?,?,DATETIME('now'))''',
            (user_id, date, ml, source)
        )

def daily_water_total(db_path: str, user_name: str, date: str) -> int:
    with get_conn(db_path) as c:
        cur = c.cursor()
        cur.execute("SELECT id FROM users WHERE name=?", (user_name,))
        row = cur.fetchone()
        if not row:
            return 0
        uid = row[0]
        cur.execute("SELECT COALESCE(SUM(ml),0) FROM water_intake WHERE user_id=? AND date=?", (uid, date))
        total = cur.fetchone()[0]
        return int(total or 0)

def steps_on_date(db_path: str, user_name: str, date: str) -> int:
    with get_conn(db_path) as c:
        cur = c.cursor()
        cur.execute("SELECT id FROM users WHERE name=?", (user_name,))
        r = cur.fetchone()
        if not r:
            return 0
        uid = r[0]
        cur.execute("SELECT steps FROM activities WHERE user_id=? AND date=? ORDER BY id DESC LIMIT 1", (uid, date))
        r2 = cur.fetchone()
        return int(r2[0]) if r2 and r2[0] is not None else 0

def weather_on_date(db_path: str, date: str, user_name: str = None):
    """Get weather data for a specific date, optionally filtered by user's city"""
    with get_conn(db_path) as c:
        cur = c.cursor()
        
        # If user_name is provided, try to get weather for user's city first
        if user_name:
            # Get user's city
            cur.execute("SELECT city FROM users WHERE name=?", (user_name,))
            user_result = cur.fetchone()
            
            if user_result and user_result[0]:
                user_city = user_result[0]
                # Try to get weather for user's city
                cur.execute("""
                    SELECT temp_max, temp_min, humidity, wind_speed, condition, city 
                    FROM weather 
                    WHERE date=? AND city=? 
                    ORDER BY id DESC LIMIT 1
                """, (date, user_city))
                weather_result = cur.fetchone()
                
                if weather_result:
                    return weather_result
        
        # Fallback: get any weather for the date
        cur.execute("""
            SELECT temp_max, temp_min, humidity, wind_speed, condition, city 
            FROM weather 
            WHERE date=? 
            ORDER BY id DESC LIMIT 1
        """, (date,))
        return cur.fetchone()

def sleep_on_date(db_path: str, user_name: str, date: str) -> float:
    with get_conn(db_path) as c:
        cur = c.cursor()
        cur.execute("SELECT id FROM users WHERE name=?", (user_name,))
        r = cur.fetchone()
        if not r:
            return 0.0
        uid = r[0]
        cur.execute("SELECT sleep_hours FROM activities WHERE user_id=? AND date=? ORDER BY id DESC LIMIT 1", (uid, date))
        r2 = cur.fetchone()
        return float(r2[0]) if r2 and r2[0] is not None else 0.0

def tail(db_path: str, table: str, n: int = 5):
    sql = _TAIL_SQL.get(table)
    if not sql:
        raise InvalidTableError(f"Invalid table name: {table}")
    with get_conn(db_path) as c:
        cur = c.cursor()
        cur.execute(sql, (n,))
        return cur.fetchall()
