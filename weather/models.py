from django.db import models
from django.utils import timezone

class Location(models.Model):
  name = models.CharField(max_length=200, db_index=True)
  display_name = models.CharField(max_length=400, blank=True)
  latitude = models.FloatField()
  longitude = models.FloatField()
  country = models.CharField(max_length=100, blank=True)
  geocoded_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.display_name or self.name

class WeatherQuery(models.Model):
  # a user request to fetch weather for a location/date-range
  location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='queries')
  start_date = models.DateField()
  end_date = models.DateField()
  created_at = models.DateTimeField(default=timezone.now)
  requester = models.CharField(max_length=150, blank=True)  # optional: username/email
  raw_response = models.JSONField(null=True, blank=True)  # Full API response (audit)
  notes = models.TextField(blank=True)

  class Meta:
    indexes = [
      models.Index(fields=['start_date','end_date']),
    ]

class WeatherRecord(models.Model):
  # one row per date (normalized)
  location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='weather_records')
  date = models.DateField(db_index=True)
  temp_c = models.FloatField(null=True, blank=True)
  temp_f = models.FloatField(null=True, blank=True)
  description = models.CharField(max_length=200, blank=True)
  source_query = models.ForeignKey(WeatherQuery, on_delete=models.SET_NULL, null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    unique_together = ('location','date')
    indexes = [
      models.Index(fields=['location','date']),
    ]
