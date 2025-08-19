import requests
from .models import Location
from difflib import get_close_matches

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "WeatherApp/1.0"

def get_or_create_location(query: str):
  query = query.strip()
  # 1) exact case-insensitive match
  qs = Location.objects.filter(name__iexact=query)
  if qs.exists():
    return qs.first()

  # 2) fuzzy match against stored Location names
  all_names = list(Location.objects.values_list('name', flat=True))
  if all_names:
    matches = get_close_matches(query, all_names, n=1, cutoff=0.75)
    if matches:
      return Location.objects.get(name=matches[0])

  # 3) query Nominatim
  params = {
    'q': query,
    'format': 'json',
    'limit': 1,
    'addressdetails': 1,
  }
  headers = {'User-Agent': USER_AGENT}
  resp = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)
  if resp.status_code != 200 or not resp.json():
    raise ValueError("Location not found; try a different query or spelling.")

  data = resp.json()[0]
  lat = float(data['lat'])
  lon = float(data['lon'])
  address = data.get('display_name', query)
  address_comp = data.get('address', {})
  country = address_comp.get('country', '')

  # save to DB
  loc = Location.objects.create(
    name=query,
    display_name=address,
    latitude=lat,
    longitude=lon,
    country=country
  )
  return loc
