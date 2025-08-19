from rest_framework import serializers
from .models import WeatherQuery, WeatherRecord, Location

class LocationSerializer(serializers.ModelSerializer):
  class Meta: model = Location; fields = '__all__'

class WeatherRecordSerializer(serializers.ModelSerializer):
  class Meta: model = WeatherRecord; fields = '__all__'

class WeatherQuerySerializer(serializers.ModelSerializer):
  location = LocationSerializer()
  class Meta: model = WeatherQuery; fields = '__all__'
