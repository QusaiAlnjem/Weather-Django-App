import requests
from django.conf import settings

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
OPENWEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

def fetch_weather_for_range(lat, lon, start_date, end_date):
  params = {
    "latitude": lat,
    "longitude": lon,
    "start_date": start_date.isoformat(),
    "end_date": end_date.isoformat(),
    "daily": "temperature_2m_min,temperature_2m_max,weathercode",
    "timezone": "UTC"
  }
  r = requests.get(OPEN_METEO_URL, params=params, timeout=15)
  r.raise_for_status()
  return r.json()

def fetch_openweather_forecast(lat, lon):
  """
  Fetch the 5-day / 3-hour forecast from OpenWeatherMap.
  Returns the JSON.
  """
  api_key = getattr(settings, "API_KEY", None)
  if not api_key:
    raise RuntimeError("Missing settings.API_KEY for OpenWeatherMap forecast.")

  params = {
    "lat": lat,
    "lon": lon,
    "appid": api_key,
    "units": "metric"
  }
  r = requests.get(OPENWEATHER_FORECAST_URL, params=params, timeout=15)
  r.raise_for_status()
  return r.json()

def parse_api_daily(api_json):
  """Return list of { 'date': 'YYYY-MM-DD', 'temp_c': ..., 'description': ... }"""
  days = []
  daily = api_json.get('daily', {})
  times = daily.get('time', [])
  tmin = daily.get('temperature_2m_min', [])
  tmax = daily.get('temperature_2m_max', [])
  codes = daily.get('weathercode', [])

  for i, d in enumerate(times):
    minv = tmin[i] if i < len(tmin) else None
    maxv = tmax[i] if i < len(tmax) else None
    temp_c = None
    if minv is not None and maxv is not None:
      temp_c = round((minv + maxv) / 2.0, 1)
    description = f"weathercode:{codes[i]}" if i < len(codes) else ""
    days.append({
      'date': d,
      'temp_c': temp_c,
      'description': description
    })
  return days
