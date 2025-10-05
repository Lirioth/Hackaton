import datetime as dt, random
from .db import add_water_intake, get_conn, upsert_activity, upsert_user


def _activity_row_count(db_path: str, user: str, date: str) -> int:
    with get_conn(db_path) as c:
        cur = c.cursor()
        cur.execute("SELECT id FROM users WHERE name=?", (user,))
        row = cur.fetchone()
        if not row:
            return 0
        cur.execute("SELECT COUNT(*) FROM activities WHERE user_id=? AND date=?", (row[0], date))
        count = cur.fetchone()[0]
        return int(count or 0)


def _demonstrate_repeat_log(db_path: str, user: str, date: str, steps: int, calories: int, mood: int, notes: str, sleep: float):
    upsert_activity(db_path, user, date, steps, calories, mood, notes, sleep)
    total = _activity_row_count(db_path, user, date)
    print(f"[seed] Re-logged activity for {user} on {date}; rows now: {total} (expected 1).")


def seed_user(db_path: str, name="Kevin", age=30, sex="M", height_cm=166, weight_kg=66, activity_level="light"):
    upsert_user(db_path, name, age, sex, height_cm, weight_kg, activity_level)


def seed_random(db_path: str, user: str, days: int = 21):
    today = dt.date.today()
    for i in range(days):
        day = today - dt.timedelta(days=i)
        steps = random.randint(3000, 15000)
        calories = random.randint(1600, 2800)
        mood = random.randint(2, 5)
        notes = random.choice(["", "Night run", "Gym + walk", "Active rest", "Light cardio"])
        sleep = round(random.uniform(5.0, 9.0), 2)
        upsert_activity(db_path, user, day.isoformat(), steps, calories, mood, notes, sleep)
        for _ in range(random.randint(4, 10)):
            ml = random.choice([150, 200, 250, 300, 350, 400, 500, 600])
            source = random.choice(["glass", "bottle", "thermos", "fountain"])
            add_water_intake(db_path, user, day.isoformat(), ml, source)
    if days > 0:
        verify_steps = random.randint(3000, 15000)
        verify_calories = random.randint(1600, 2800)
        verify_mood = random.randint(2, 5)
        verify_notes = "Updated log after repeat entry"
        verify_sleep = round(random.uniform(5.0, 9.0), 2)
        _demonstrate_repeat_log(
            db_path,
            user,
            today.isoformat(),
            verify_steps,
            verify_calories,
            verify_mood,
            verify_notes,
            verify_sleep,
        )


def seed_faker(db_path: str, user: str, days: int = 21):
    try:
        from faker import Faker
    except Exception:
        print("[seed] Faker not installed, using random generator.")
        return seed_random(db_path, user, days)
    fake = Faker()
    today = dt.date.today()
    for i in range(days):
        day = today - dt.timedelta(days=i)
        base = 7000 + int(3000 * fake.pyfloat(left_digits=1, right_digits=2, positive=True))
        steps = int(base + fake.pyint(min_value=-2500, max_value=2500))
        calories = int(1800 + fake.pyint(min_value=-400, max_value=600))
        mood = fake.pyint(min_value=1, max_value=5)
        notes = fake.sentence(nb_words=6)
        sleep = round(fake.pyfloat(left_digits=1, right_digits=2, positive=True, max_value=10), 2)
        upsert_activity(db_path, user, day.isoformat(), steps, calories, mood, notes, sleep)
        for _ in range(fake.pyint(min_value=4, max_value=10)):
            ml = fake.random_element(elements=(150, 200, 250, 300, 350, 400, 500, 600))
            source = fake.random_element(elements=("glass", "bottle", "thermos", "fountain"))
            add_water_intake(db_path, user, day.isoformat(), ml, source)
    if days > 0:
        verify_steps = int(7000 + fake.pyint(min_value=-1500, max_value=2000))
        verify_calories = int(1800 + fake.pyint(min_value=-300, max_value=450))
        verify_mood = fake.pyint(min_value=1, max_value=5)
        verify_notes = "Updated log after repeat entry"
        verify_sleep = round(fake.pyfloat(left_digits=1, right_digits=2, positive=True, max_value=10), 2)
        _demonstrate_repeat_log(
            db_path,
            user,
            today.isoformat(),
            verify_steps,
            verify_calories,
            verify_mood,
            verify_notes,
            verify_sleep,
        )
