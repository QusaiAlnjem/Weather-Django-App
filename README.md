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

## 📦 Requirements

Main dependencies:
Django
djangorestframework
requests
torch
transformers
See full list in requirements.txt

---

## 🖼️ Images

<img width="1919" height="925" alt="Screenshot 2025-08-19 173040" src="https://github.com/user-attachments/assets/9d5f0d93-5fbc-4e3a-bec9-f2eb2afe5b93" />
<img width="1900" height="923" alt="Screenshot 2025-08-19 173103" src="https://github.com/user-attachments/assets/2ca7cced-3d2e-4b3b-a694-186b4bd660a0" />
<img width="1898" height="926" alt="Screenshot 2025-08-19 173202" src="https://github.com/user-attachments/assets/90395714-591f-4d34-8ed0-ed6764ebe90e" />
<img width="1898" height="925" alt="Screenshot 2025-08-19 173236" src="https://github.com/user-attachments/assets/69dfd629-d152-4d60-90ae-398f45d358ab" />
<img width="862" height="688" alt="Screenshot 2025-08-19 173412" src="https://github.com/user-attachments/assets/986c2113-e424-4096-a4f5-afd9fc44e3ff" />
<img width="872" height="793" alt="Screenshot 2025-08-19 173438" src="https://github.com/user-attachments/assets/b7669f2a-569c-4061-9089-f5391757dcff" />
<img width="1901" height="926" alt="Screenshot 2025-08-19 173510" src="https://github.com/user-attachments/assets/f7d08123-df3c-412e-821b-646f78204c45" />
<img width="1899" height="924" alt="Screenshot 2025-08-19 173525" src="https://github.com/user-attachments/assets/80842411-27ea-4c6f-943c-bc3d41b184cf" />

