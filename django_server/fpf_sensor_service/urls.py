from django.urls import path
from .views import post_sensor_interval

urlpatterns = [
    path('sensorInterval/<str:sensorId>', post_sensor_interval, name='update_sensor_interval'),
]
