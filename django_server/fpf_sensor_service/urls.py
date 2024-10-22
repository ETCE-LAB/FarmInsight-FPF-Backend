from django.urls import path
from . import views

urlpatterns = [
    path('sensorInterval/<str:sensorId>', views.update_sensor_interval, name='update_sensor_interval'),
]
