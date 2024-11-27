from django.urls import path
from fpf_sensor_service.views import post_sensor, get_available_sensor_types, SensorView


urlpatterns = [
    path('sensors/types', get_available_sensor_types, name='get_available_sensor_types'),
    path('sensors', post_sensor, name='post_sensor'),
    path('sensors/<str:sensor_id>', SensorView.as_view(), name='sensor_views'),
]
