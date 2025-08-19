// Displaying Weather
class WeatherApp {
  constructor() {
    this.locationInput = document.getElementById('searchInput');
    this.searchBtn = document.getElementById('searchBtn');
    this.currentLocationBtn = document.getElementById('locationBtn');
    this.loading = document.getElementById('loading');
    this.weatherResult = document.getElementById('weatherResult');
    this.locMessage = document.getElementById('locMessage');
    this.errorDiv = document.getElementById('errorDiv');
    this.learnMoreBtn = document.getElementById('learnMoreBtn');
    this.closeWrnBtn = document.getElementById('closeWarningBtn');
    this.warningNotification = document.getElementById('warningNotification');
    this.warningDetails = document.getElementById('warningDetails');


    this.initEventListeners();
  }

  initEventListeners() {
    // Search button click
    this.searchBtn.addEventListener('click', () => {
      this.searchWeather(this.locationInput.value.trim());
    });

    // Enter key press in input
    this.locationInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.searchWeather(this.locationInput.value.trim());
      }
    });

    // Current Location Request Button
    this.currentLocationBtn.addEventListener('click', () => {
      check = localStorage.getItem('userLocation')
      if (check === null || check === '') {
        this.locMessage.style.display = 'block';
        geolocationAccess();
      }
      else {
        this.locMessage.style.display = 'none';
        this.searchWeather(localStorage.getItem('userLocation'));
      }
    })

    // Warning Section Clicks
    this.learnMoreBtn.addEventListener('click', () => {
      this.toggleWarningDetails();
    });
    this.closeWrnBtn.addEventListener('click', () => {
      this.hideWarningSection();
    });

  }

  // Get CSRF token from cookie
  getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // POST request to backend for weather search
  async searchWeather(loc) {
    const location = loc;
    
    if (!location) {
      this.showError('Enter a location OR allow current location access.');
      return;
    }

    try {
      this.showLoading(true);
      this.hideError();
      this.hideWeatherResult();

      const csrftoken = this.getCookie('csrftoken');
      
      // Send POST request to Django backend
      const response = await fetch(window.ENDPOINTS.getWeather, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
          location: location
        })
      });
      const data = await response.json();

      if (data.success) {
        this.displayWeatherData(data.data);
        this.displayForecastData(data.forecast || []);
        this.processAndDisplayWarnings(data.data, data.forecast);
      } 
      else {
        this.showError(data.error || 'Failed to fetch weather data');
      }

    } 
    catch (error) {
      console.error('Error:', error);
      this.showError('Network error. Please try again.');
    } 
    finally {
      this.showLoading(false);
    }
  }

  displayWeatherData(data) {
    // Populate current weather data
    document.getElementById('locationName').textContent = `${data.location}, ${data.country}`;
    document.getElementById('addressType').textContent = `📍 ${data.address_type}`;
    document.getElementById('temperature').textContent = `${Math.round(data.temperature)}°C`;
    document.getElementById('description').textContent = data.description;
    document.getElementById('feelsLike').textContent = `${Math.round(data.feels_like)}°C`;
    document.getElementById('humidity').textContent = `${data.humidity}%`;
    document.getElementById('windSpeed').textContent = `${data.wind_speed} km/h`;
    document.getElementById('visibility').textContent = `${data.visibility} km`;
    document.getElementById('country').textContent = data.country;
    
    // Format and display sunrise/sunset
    const sunrise = new Date(data.sunrise * 1000).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
    const sunset = new Date(data.sunset * 1000).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
    document.getElementById('sunrise').textContent = sunrise;
    document.getElementById('sunset').textContent = sunset;
    
    // Set weather icon
    const iconUrl = `https://openweathermap.org/img/wn/${data.icon}@2x.png`;
    document.getElementById('weatherIcon').src = iconUrl;
    
    this.showWeatherResult();
  }

  displayForecastData(forecast) {
    const forecastContainer = document.getElementById('forecastContainer');
    
    if (!forecastContainer || forecast.length === 0) {
      return;
    }

    // Clear existing forecast
    forecastContainer.innerHTML = '';

    // Add forecast title
    const forecastTitle = document.createElement('h3');
    forecastTitle.className = 'forecast-title';
    forecastTitle.textContent = 'Weather Forecast';
    forecastContainer.appendChild(forecastTitle);

    // Create forecast grid
    const forecastGrid = document.createElement('div');
    forecastGrid.className = 'forecast-grid';

    forecast.forEach(day => {
      const dayElement = this.createForecastDayElement(day);
      forecastGrid.appendChild(dayElement);
    });

    forecastContainer.appendChild(forecastGrid);
  }

  createForecastDayElement(day) {
    const dayElement = document.createElement('div');
    dayElement.className = 'forecast-day';
    
    // Format date
    const date = new Date(day.date);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    
    let displayDay = day.day_name;
    if (date.toDateString() === tomorrow.toDateString()) {
      displayDay = 'Tomorrow';
    }

    dayElement.innerHTML = `
      <div class="forecast-day-name">${displayDay}</div>
      <div class="forecast-date">${date.getMonth() + 1}/${date.getDate()}</div>
      <img class="forecast-icon" src="https://openweathermap.org/img/wn/${day.icon}@2x.png" alt="${day.description}" />
      <div class="forecast-temps">
        <span class="forecast-high">${Math.round(day.max_temp)}°</span>
        <span class="forecast-low">${Math.round(day.min_temp)}°</span>
      </div>
      <div class="forecast-desc">${day.description}</div>
      <div class="forecast-details">
        <div class="forecast-detail">🌡️ Feels ${Math.round(day.feels_like)}°</div>
        <div class="forecast-detail">☔ ${day.rain_chance}%</div>
        <div class="forecast-detail">💧 ${day.humidity}%</div>
        <div class="forecast-detail">💨 ${day.wind_speed}m/s</div>
      </div>
    `;

    return dayElement;
  }

  processAndDisplayWarnings(currentWeather, forecast) {
    const allWarnings = [];
    let totalWarningCount = 0;

    // Process current weather warnings
    if (currentWeather["warnings"] && currentWeather["warnings"].length > 1) {
      const dayName = currentWeather["warnings"][0];
      const warnings = currentWeather["warnings"].slice(1);
      if (warnings.length > 0) {
        allWarnings.push({ day: dayName, warnings: warnings });
        totalWarningCount += warnings.length;
      }
    }

    // Process forecast warnings
    forecast.forEach(day => {
      if (day["warnings"] && day["warnings"].length > 1) {
        const dayName = day["warnings"][0];
        const warnings = day["warnings"].slice(1);
        if (warnings.length > 0) {
          allWarnings.push({ day: dayName, warnings: warnings });
          totalWarningCount += warnings.length;
        }
      }
    });

    // Display warnings if any exist
    if (totalWarningCount > 0) {
      this.displayWarnings(allWarnings, totalWarningCount);
    }
  }

  displayWarnings(warningsData, totalCount) {
    // Update warning count
    document.getElementById('warningCount').textContent = totalCount;

    // Build warnings HTML
    const warningList = document.getElementById('warningList');
    warningList.innerHTML = '';

    warningsData.forEach((dayWarnings, index) => {
      // Create day section
      const daySection = document.createElement('div');
      daySection.className = 'warning-day-section';

      // Day title
      const dayTitle = document.createElement('h4');
      dayTitle.className = 'warning-day-title';
      dayTitle.textContent = dayWarnings.day;
      daySection.appendChild(dayTitle);

      // Day warnings
      const warningsList = document.createElement('ul');
      warningsList.className = 'warning-day-list';

      dayWarnings["warnings"].forEach(warning => {
        const warningItem = document.createElement('li');
        warningItem.className = 'warning-item';
        warningItem.textContent = warning;
        warningsList.appendChild(warningItem);
      });

      daySection.appendChild(warningsList);

      // Add separator if not the last item
      if (index < warningsData.length - 1) {
        const separator = document.createElement('div');
        separator.className = 'warning-separator';
        daySection.appendChild(separator);
      }

      warningList.appendChild(daySection);
    });

    this.showWarningSection();
  }

  showWarningSection() {
    this.warningNotification.classList.remove('hidden');
    this.warningDetails.classList.remove('expanded');
    this.learnMoreBtn.textContent = 'Learn More';
  }

  hideWarningSection() {
    this.warningNotification.classList.add('hidden');
    this.warningDetails.classList.remove('expanded');
    this.learnMoreBtn.textContent = 'Learn More';
  }

  toggleWarningDetails() {
    const expanded = this.warningDetails.classList.toggle('expanded');
    this.learnMoreBtn.textContent = expanded ? 'Show Less' : 'Learn More';
  }

  showLoading(show) {
    this.loading.style.display = show ? 'block' : 'none';
    this.searchBtn.disabled = show;
    this.searchBtn.textContent = show ? 'Searching...' : '🔍';
  }

  showWeatherResult() {
    this.weatherResult.style.display = 'block';
  }

  hideWeatherResult() {
    this.weatherResult.style.display = 'none';
  }

  showError(message) {
    document.getElementById('errorMessageDiv').textContent = message;
    this.errorDiv.classList.add('show');
  }
  
  hideError() {
    document.getElementById('errorMessageDiv').textContent = "";
    this.errorDiv.classList.remove('show');
  }
}
//-----------------------------------------

// Initialization
document.addEventListener('DOMContentLoaded', () => {
  check = localStorage.getItem('userLocation');
  if (check === null || check === '') { geolocationAccess() }
  new WeatherApp();
});
//-----------------------------------------

// Geolocation Access Permission
function geolocationAccess() {
  if ("geolocation" in navigator) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const userLocation = `${position.coords.latitude}, ${position.coords.longitude}`
        localStorage.setItem('userLocation', userLocation)
      },
      () => {
        alert("Location access denied. Please allow location to get local weather.");
      }
    );
  } 
  else {
    alert("Geolocation is not supported by your browser.");
  }
}
//-----------------------------------------

// Animation
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    document.body.style.backgroundSize = '400% 400%';
    document.body.style.animation = 'gradientShift 15s ease infinite';
  }, 1000);
});
const style = document.createElement('style');
style.textContent = `
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        25% { background-position: 100% 50%; }
        50% { background-position: 100% 100%; }
        75% { background-position: 0% 100%; }
    }
`;
document.head.appendChild(style);
//-----------------------------------------