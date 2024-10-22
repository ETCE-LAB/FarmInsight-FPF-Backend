from django.contrib import admin
from .models import SensorConfig, SensorMeasurement

admin.site.register(SensorConfig)
admin.site.register(SensorMeasurement)
