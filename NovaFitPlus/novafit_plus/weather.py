import requests
from typing import Optional, Tuple

def geocode_city(city: str, country: Optional[str] = None, timeout: int = 10) -> Tuple[float, float, str]:
    q = city if not country else f"{city}, {country}"
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": q, "count": 1, "language": "en", "format": "json"}
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if not data.get("results"):
        raise ValueError(f"City not found: {q}")
    res = data["results"][0]
    return float(res["latitude"]), float(res["longitude"]), res.get("name", city)

def fetch_daily_forecast(lat: float, lon: float, days: int = 1, timeout: int = 10):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,relative_humidity_2m_mean,windspeed_10m_max,weathercode",
        "forecast_days": max(1, min(days, 16)),
        "timezone": "auto"
    }
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()

WCODE = {
    0: "Clear sky", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog", 51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain", 71: "Light snow", 73: "Snow", 75: "Heavy snow",
    95: "Thunderstorm", 99: "Severe thunderstorm"
}

def code_to_text(code: int) -> str:
    return WCODE.get(int(code), f"Code {code}")
