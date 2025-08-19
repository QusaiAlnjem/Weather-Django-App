# 🌦️ Django Weather App (with SQLite3 & ML Extension)

A weather application built with **Django**, **Python** **JavaScript**, **APIs**, and **SQL** that allows users to:
- See current location weather with 5 days forecast.
- Check the weather of any location they like.
- Enter location in different formats **(Zip Code, GPS Coordinates, Country, City, Town)**.
- Use warning notifications to pay attention to a critical weather warnings that includes **(Temperature, Feels Like, Humadity, Wind Speed, Visibility)**.
- Create and save weather queries by **location** and **date range**.
- Automatically fetch and store forecast data from the **OpenWeather API**.
- Display the **most temperate day** within each saved query.
- Update or delete queries and their daily records directly from the main page.

---

## 🚀 Features
- **CRUD Operations**  
  - Create new weather queries (location + date range).  
  - Read & display saved queries with forecast results.  
  - Update temperatures of individual records.  
  - Delete queries.  

- **Weather Data Integration**  
  - Fetches forecast data from **OpenWeather API**.  
  - Displays weather for current location or different locations.
  - Shows crititcal warnings about the weather.

- **Database Persistence**  
  - Uses **SQLite3** with Django for storing locations, queries, and weather records.  

- **Machine Learning Add-on**  
  - Includes optional ML utility (`ml_utils.py`) powered by **PyTorch** & **Transformers**.  
  - Classifies addresses (e.g., city or zip code).  

---

## 📂 Project Structure
venv/  
│  Scripts/
│  │
│  ├── weather/ # Main Django app
│  │ ├── migrations/ # DB migrations
│  │ ├── templates/weather/ # HTML templates
│  │ │ └── home.html
│  │ ├── static/weather/ # CSS/JS
│  │ │ └── home.js
│  │ │ └── home.css
│  │ ├── models.py # Location, WeatherQuery, WeatherRecord
│  │ ├── views.py # CRUD + weather logic
│  │ ├── urls.py # App routes
│  │ ├── fetch_weather.py # OpenWeather API calls
│  │ ├── geocode.py # Location geocoding
│  │ ├── ml_utils.py # ML/NLP classifier
│  │ └── serializers.py # DRF serializers
│  │
│  ├── weather_app/ # Django project root
│  │ ├── settings.py
│  │ ├── urls.py
│  │ └── wsgi.py
│  │
│  ├── manage.py
│  ├── requirements.txt
│  └── README.md


## 📦 Requirements

Main dependencies:
Django
djangorestframework
requests
torch
transformers
See full list in requirements.txt
