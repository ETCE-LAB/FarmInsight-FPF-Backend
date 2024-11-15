from django.urls import path
from fpf_sensor_service.views import post_sensor_interval, get_available_sensor_types

urlpatterns = [
    path('sensorInterval/<str:sensorId>', post_sensor_interval, name='update_sensor_interval'),
    path('sensors/types', get_available_sensor_types, name='get_available_sensor_types'),
]
