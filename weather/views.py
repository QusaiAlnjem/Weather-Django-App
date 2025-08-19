from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

""" Main Page """
COMFORT_TEMP = 20.0 # °C target for "most temperate" day
MAX_DAYS = 5

def build_home_context():
  """Return the same context that the home view and error-rendering branches expect."""
  queries = WeatherQuery.objects.select_related('location').order_by('-created_at')

  queries_with_best = []
  for q in queries:
    records = list(WeatherRecord.objects.filter(source_query=q).order_by('date'))
    best_day = None
    best_temp = None
    if records:
      valid_records = [r for r in records if r.temp_c is not None]
      if valid_records:
        best_rec = min(valid_records, key=lambda r: abs((r.temp_c or 0) - COMFORT_TEMP))
        best_day = best_rec.date
        best_temp = best_rec.temp_c
    queries_with_best.append({
      'query': q,
      'best_day': best_day,
      'best_temp': best_temp,
      'records': records,
    })
  return {'queries_with_best': queries_with_best}

@ensure_csrf_cookie
@require_http_methods(["GET"])
def home(request):
    context = build_home_context()
    return render(request, 'weather/home.html', context)
""" --------- """



""" Weather Processing / API fetching - Logic """
import re
import json
import requests
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from .ml_utils import classify_address_type
from datetime import datetime
from collections import Counter


@csrf_protect
@require_http_methods(["POST"])
def get_weather(request):
  try:
    data = json.loads(request.body)
    location = data.get('location', '').strip().title()
    
    if not location:
      return JsonResponse({
      'success': False,
      'error': 'Location is Required!'
    }, status=400)

  except json.JSONDecodeError:
      return JsonResponse({
        'success': False,
        'error': 'Invalid Json Data!'
      }, status=400)
    
  
  # Using The AI Model To Classify
  address_type = classify_address_type(location)

  # Fetching From API
  try:
    weather_data = process_weather_request(location, address_type)
  except Exception as e:
    print(e)

  if weather_data and weather_data.get('success'):
    return JsonResponse({
      'success': True,
      'data': weather_data['data'],
      'forecast': weather_data.get('forecast', []),
      'error': ""
    })
  else:
    return JsonResponse({
      'success': False,
      'error': weather_data.get('error', 'Unknown error occurred')
    })
  
def process_weather_request(location: str, address_type: str):
  try:
    API_KEY = settings.API_KEY
    weather_url = "http://api.openweathermap.org/data/2.5/weather"
    forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
    
    # Prepare parameters based on address type
    if address_type == 'Zip Code':
      # Handle zip code format
      params = {
        'zip': location,
        'appid': API_KEY,
        'units': 'metric'
      }
    elif address_type == 'GPS Coordinates':
      # Parse GPS coordinates (lat,lon format)
      coords = parse_gps_coordinates(location)
      if coords:
        params = {
          'lat': coords['lat'],
          'lon': coords['lon'],
          'appid': API_KEY,
          'units': 'metric'
        }

    elif address_type == 'Landmarks':
      geo = geocode_landmark_nominatim(location)
      if not geo:
        return {"success": False, "error": "Could not resolve landmark"}
      params = {
        'q': geo['city'],
        'appid': API_KEY,
        'units': 'metric'
      }

    else:
      params = {
        'q': location,
        'appid': API_KEY,
        'units': 'metric'
      }
    
    # Weather API request
    current_response = requests.get(weather_url, params=params)
    
    if current_response.status_code != 200:
      return {
        'success': False,
        'error': f'Weather API error: {current_response.status_code}'
      }
    
    current_data = current_response.json()
    
    # Forecast API request
    forecast_response = requests.get(forecast_url, params=params)
    
    # Process current weather
    weather_info = {
        'location': current_data['name'],
        'country': current_data['sys']['country'],
        'temperature': current_data['main']['temp'],
        'feels_like': current_data['main']['feels_like'],
        'description': current_data['weather'][0]['description'],
        'humidity': current_data['main']['humidity'],
        'wind_speed': current_data['wind']['speed'] * 3.6,
        'visibility': current_data.get('visibility', 0) / 1000,
        'icon': current_data['weather'][0]['icon'],
        'sunrise': current_data['sys']['sunrise'],
        'sunset': current_data['sys']['sunset'],
        'address_type': address_type,
        'warnings': None
    }

    # Warnings Check
    weather_info['warnings'] = warnings_check(weather_info, "Today")
    
    # Process forecast data
    forecast_data = []
    if forecast_response.status_code == 200:
      forecast_json = forecast_response.json()
      forecast_data = process_forecast_data(forecast_json)
    
    return {
      'success': True,
      'data': weather_info,
      'forecast': forecast_data,
      'error': ""
    }
        
  except requests.RequestException as e:
    return {
      'success': False,
      'data': {},
      'forecast': [],
      'error': f'Network error: {str(e)}'
    }
  except Exception as e:
    return {
      'success': False,
      'data': {},
      'forecast': [],
      'error': f'Processing error: {str(e)}'
    }

def process_forecast_data(forecast_json):
  daily = {}  # keyed by 'YYYY-MM-DD'
  today = datetime.now().date()

  for item in forecast_json.get('list', []):
    dt = datetime.fromtimestamp(item['dt'])
    date_obj = dt.date()
    if date_obj == today:
      continue  # skip today

    date_key = date_obj.isoformat()

    if date_key not in daily:
      daily[date_key] = {
        'day_name': dt.strftime('%A'),
        'temp_sum': 0.0,
        'temp_count': 0,
        'temp_max': float('-inf'),
        'temp_min': float('inf'),
        'humidity_sum': 0.0,
        'wind_sum_kmh': 0.0,
        'feels_sum': 0.0,
        'rain_sum': 0.0,
        'visibility': item.get('visibility', 0) / 1000,
        'count': 0,
        'desc_counter': Counter(),
        'icon_counter': Counter()
      }

    d = daily[date_key]

    temp = item['main']['temp']
    d['temp_sum'] += temp
    d['temp_count'] += 1
    d['temp_max'] = max(d['temp_max'], temp)
    d['temp_min'] = min(d['temp_min'], temp)

    humidity = item['main'].get('humidity', 0)
    d['humidity_sum'] += humidity

    wind_ms = item.get('wind', {}).get('speed', 0.0)
    d['wind_sum_kmh'] += (wind_ms * 3.6)

    feels = item['main'].get('feels_like', temp)
    d['feels_sum'] += feels

    # 'pop' is probability of precipitation (0..1) in forecast API
    rain_prob = item.get('pop', 0) * 100
    d['rain_sum'] += rain_prob

    d['count'] += 1

    desc = item['weather'][0].get('description', '')
    icon = item['weather'][0].get('icon', '')
    d['desc_counter'][desc] += 1
    d['icon_counter'][icon] += 1

  processed_forecasts = []
  for date_key in sorted(daily.keys()):
    d = daily[date_key]

    avg_temp = round(d['temp_sum'] / d['temp_count'], 1)
    max_temp = round(d['temp_max'], 1)
    min_temp = round(d['temp_min'], 1)
    avg_humidity = round(d['humidity_sum'] / d['temp_count'])
    avg_wind = round(d['wind_sum_kmh'] / d['temp_count'], 1)
    avg_feels_like = round(d['feels_sum'] / d['temp_count'], 1)
    avg_rain_chance = round(d['rain_sum'] / d['temp_count'])

    most_common_desc = d['desc_counter'].most_common(1)[0][0] if d['desc_counter'] else ''
    most_common_icon = d['icon_counter'].most_common(1)[0][0] if d['icon_counter'] else ''

    processed_forecasts.append({
      'date': date_key,
      'day_name': d['day_name'],
      'temperature': avg_temp,
      'max_temp': max_temp,
      'min_temp': min_temp,
      'feels_like': avg_feels_like,
      'description': most_common_desc,
      'icon': most_common_icon,
      'humidity': avg_humidity,
      'wind_speed': avg_wind,
      'rain_chance': avg_rain_chance,
      'visibility': d['visibility'],
      'warnings': None
    })

    processed_forecasts[-1]['warnings'] = warnings_check(processed_forecasts[-1], d['day_name'])

  return processed_forecasts

def parse_gps_coordinates(location):
  try:
    coords = re.split(r'[,\s]+', location.strip())
    
    if len(coords) == 2:
      lat = float(coords[0])
      lon = float(coords[1])
      
      # Validate coordinate ranges
      if -90 <= lat <= 90 and -180 <= lon <= 180:
        return {'lat': lat, 'lon': lon}
  
    return None

  except (ValueError, IndexError):
    return None

def geocode_landmark_nominatim(landmark):
  """
  Convert a landmark name to coordinates (lat, lon) and city.
  """
  url = "https://nominatim.openstreetmap.org/search"
  params = {
    "q": landmark,
    "format": "json",
    "limit": 1,
    "addressdetails": 1
  }
  headers = {
    "User-Agent": "WeatherAPP/1.0"  # Nominatim requires a User-Agent
  }
  response = requests.get(url, params=params, headers=headers)
  if response.status_code == 200 and response.json():
    data = response.json()[0]
    lat = float(data["lat"])
    lon = float(data["lon"])

    # Try to get city from address components
    address = data.get("address", {})
    city = address.get("city") or address.get("town") or address.get("village") or address.get("state")
    
    return {"lat": lat, "lon": lon, "city": city or data.get("display_name")}
  
  return None

def warnings_check(data, day):
  warnings = [day]

  if data['feels_like'] > 45:
    warnings.append("⚠️ Feels like temperature is dangerously high! Risk of heatstroke.")

  if data['temperature'] > 40:
    warnings.append("⚠️ Extreme heat detected! Stay hydrated and search for air conditioned places.")
  elif data['temperature'] < 0:
    warnings.append("⚠️ Extreme cold detected! Wear something thick.")

  if data['humidity'] > 70:
    warnings.append("⚠️ Very high humidity! It may feel hotter and cause discomfort.")

  if data['wind_speed'] > 60:
    warnings.append("⚠️ Strong winds! Risk of damage and travel disruption")

  if data['visibility'] < 2:
    warnings.append("⚠️ Poor visibility! Avoid travelling and long rides.")
  
  return warnings

""" --------------------------------------------- """



""" Database Processing CRUD - Libraries """
from django.shortcuts import redirect, get_object_or_404
from django.utils.dateparse import parse_date
from django.db import transaction
from datetime import date
from .models import Location, WeatherQuery, WeatherRecord
from .geocode import get_or_create_location
from .fetch_weather import fetch_openweather_forecast, fetch_weather_for_range, parse_api_daily

# Celsius to Fahrenheit
def c_to_f(c):
  if c is None:
    return None
  return round(c * 9.0 / 5.0 + 32.0, 1)

# -- CREATE
@require_http_methods(["POST"])
def create_query(request):
    # Get inputs
    loc_text = request.POST.get('location', '').strip()
    start_date = parse_date(request.POST.get('start_date'))
    end_date = parse_date(request.POST.get('end_date'))

    # Basic validation BEFORE any DB operation
    if not loc_text:
        ctx = build_home_context()
        ctx['error'] = 'Location is required.'
        return render(request, 'weather/home.html', ctx)

    if not (start_date and end_date):
        ctx = build_home_context()
        ctx['error'] = 'Invalid dates.'
        return render(request, 'weather/home.html', ctx)

    if start_date > end_date:
        ctx = build_home_context()
        ctx['error'] = 'Start date must be <= End date.'
        return render(request, 'weather/home.html', ctx)

    # Enforce max period length BEFORE any network or DB write
    if (end_date - start_date).days + 1 > MAX_DAYS:
        ctx = build_home_context()
        ctx['error'] = f'Maximum allowed period is {MAX_DAYS} days.'
        return render(request, 'weather/home.html', ctx)

    # Resolve location (may call external service) - OK to do after validation
    try:
        location = get_or_create_location(loc_text)
    except Exception as e:
        ctx = build_home_context()
        ctx['error'] = f'Location error: {e}'
        return render(request, 'weather/home.html', ctx)

    # Get forecast JSON (external API) - still before DB writes
    try:
        forecast_json = fetch_openweather_forecast(location.latitude, location.longitude)
    except Exception as e:
        ctx = build_home_context()
        ctx['error'] = f'Forecast API error: {e}'
        return render(request, 'weather/home.html', ctx)

    # Process forecast to daily summaries (your provided function)
    try:
        processed = process_forecast_data(forecast_json)
    except Exception as e:
        ctx = build_home_context()
        ctx['error'] = f'Failed to process forecast: {e}'
        return render(request, 'weather/home.html', ctx)

    # Filter processed days to user-specified range
    start_s = start_date.isoformat()
    end_s = end_date.isoformat()
    selected_days = [d for d in processed if start_s <= d['date'] <= end_s]

    if not selected_days:
        ctx = build_home_context()
        ctx['error'] = 'No forecast data available for that date range.'
        return render(request, 'weather/home.html', ctx)

    # All validations passed and data available -> perform DB writes within a transaction
    try:
        with transaction.atomic():
            wq = WeatherQuery.objects.create(
                location=location,
                start_date=start_date,
                end_date=end_date,
                requester=request.user.username if request.user.is_authenticated else '',
                raw_response=forecast_json
            )

            for day in selected_days:
                # convert 'YYYY-MM-DD' to date object (safe)
                try:
                    date_obj = date.fromisoformat(day['date'])
                except Exception:
                    date_obj = day['date']

                WeatherRecord.objects.update_or_create(
                    location=location,
                    date=date_obj,
                    defaults={
                        'temp_c': day.get('temperature'),
                        'temp_f': c_to_f(day.get('temperature')) if day.get('temperature') is not None else None,
                        'description': day.get('description', ''),
                        'source_query': wq
                    }
                )
    except Exception as e:
        # Any DB/external error: do NOT delete existing DB objects; just show an error
        ctx = build_home_context()
        ctx['error'] = f'Failed saving query: {e}'
        return render(request, 'weather/home.html', ctx)

    # Success -> redirect to home (which will show new query)
    return redirect('weather:home')

# -- UPDATE
@require_http_methods(["POST"])
def update_record(request, pk):
  rec = get_object_or_404(WeatherRecord, pk=pk)
  temp_c = request.POST.get('temp_c')
  if temp_c is None:
    # nothing to update; go back
    return redirect('weather:home')

  try:
    temp_c = float(temp_c)
  except ValueError:
    # show error on the detail page (simple approach)
    return render(request, 'weather/home.html', {
      'query': rec.source_query,
      'records': WeatherRecord.objects.filter(source_query=rec.source_query),
      'error': 'Invalid temperature value'
    })

  rec.temp_c = temp_c
  rec.temp_f = round(temp_c * 9/5 + 32, 1)
  rec.save()  
  # redirect back to the query detail page that contains this record
  if rec.source_query_id:
    return redirect('weather:home')
  return redirect('weather:home')

# -- DELETE
@require_http_methods(["POST"])
def delete_query(request, pk):
  wq = get_object_or_404(WeatherQuery, pk=pk)
  wq.delete()
  return redirect('weather:home')

# -- READ
@require_http_methods(["GET"])
def query_list(request):
  queries = WeatherQuery.objects.select_related('location').order_by('-created_at')
  return render(request, 'weather/home.html', {'queries': queries})

@require_http_methods(["GET"])
def query_detail(request, pk):
  q = get_object_or_404(WeatherQuery, pk=pk)
  records = WeatherRecord.objects.filter(source_query=q).order_by('date')
  return render(request, 'weather/home.html', {'query': q, 'records': records})

""" ------------------------------------ """