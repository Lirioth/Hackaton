# NovaFit Plus CLI
Serious, demo-ready Health + Weather + Hydration tracker for terminal and Tkinter GUI.

## Features
- Profile onboarding → BMI, BMR and maintenance calories.
- Log activity (steps, calories, mood, notes) + **sleep hours**.
- Water intake per intake; personalized daily target by weight, steps and weather.
- Weather via Open-Meteo (no API key), stored to SQLite.
- Analytics: KPIs, hydration adherence, **weekly/monthly sleep % vs 8h**.
- **Health Score (7d)** combining steps, hydration, sleep and mood (with small BMI adjustment).
- Exports: JSON and **Excel (.xlsx)** (sheets for profile, activities, weather, water, hydration summary).
- Optional GUI with tabs: Dashboard, Activity, Water, Weather, Analytics, Export, Profile.

## Quickstart
```bash
cd NovaFit_Plus_CLI
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m novafit_plus.app          # CLI
python -m novafit_plus.ui_tk        # GUI
```

## Menu
1) Setup/Update profile
2) Log TODAY activity (incl. sleep)
3) Log water intake
4) Daily dashboard (BMI/BMR, hydration, **sleep %, Health Score**, today's weather)
5) Fetch & save weather
6) Analytics
7) Export (JSON + Excel)
8) Seed demo data (Faker/random)
9) Tail last rows
0) Exit

## Manual QA Checklist
- Ensure the database is initialized by running `python -m novafit_plus.app` and seeding demo data if needed.
- Log an activity for today via the CLI, then repeat the same option with different values for steps or notes to overwrite the entry.
- Use option `9) Tail last rows` targeting the `activities` table to confirm only one record exists for the user/date pair and that it reflects the updated values.
- Run the seeding helper twice (e.g., `python -m novafit_plus.seed`) or re-run option `8)` to observe the `[seed] Re-logged activity...` message confirming a single row per day.

### Health Score and Sleep Percentages
- Dashboard shows **Weekly** and **Monthly** sleep percentages vs. an 8-hour target.
- A **Health Score (7 days)** combines steps, hydration, sleep and mood, with a small BMI adjustment. Scale 0–100.


### Insights tab & visual polish
- New **Insights** tab: choose 7d or 30d period, generate actionable tips (hydration remainder, sleep gap vs 8h, steps trend, weather tip) and a banded assessment (Excellent/Good/Fair/Needs attention).
- Dashboard includes **Health Score** progress bar. Simple Light/Dark theme toggle.


## Bootstrap (auto-install)
```bash
# GUI
python bootstrap.py --gui
# CLI
python bootstrap.py
```
This script creates `.venv/`, installs `requirements.txt`, and launches the app.

## CSV Export & Charts
- `Export` tab: CSV/JSON/Excel.
- `Reports` tab: generates PNG charts in `exports/charts/`:
  - `hydration_pct.png` (adherencia de hidratación)
  - `hydration_goal_vs_actual.png` (consumo real vs meta de hidratación)
  - `steps_vs_sleep.png` (relación entre pasos y sueño)
