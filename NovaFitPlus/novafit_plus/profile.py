from typing import Tuple

def bmi(weight_kg: float, height_cm: float) -> Tuple[float, str]:
    h_m = max(0.5, height_cm / 100.0)
    val = weight_kg / (h_m * h_m)
    cat = "Underweight" if val < 18.5 else "Normal" if val < 25 else "Overweight" if val < 30 else "Obese"
    return round(val, 2), cat

def bmr_mifflin(age: int, sex: str, height_cm: float, weight_kg: float) -> float:
    s = -161 if str(sex).strip().lower().startswith("f") else 5
    return round(10*weight_kg + 6.25*height_cm - 5*age + s, 1)

def maintenance_calories(bmr: float, activity_level: str = "light") -> float:
    level = (activity_level or "light").strip().lower()
    factors = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725}
    mult = factors.get(level, 1.375)
    return round(bmr * mult, 0)
