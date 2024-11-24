from django.urls import path
from fpf_sensor_service.views import post_sensor, get_available_sensor_types, put_sensor, get_sensor, post_fpf_id, \
    post_api_key


urlpatterns = [
    path('sensors/types', get_available_sensor_types, name='get_available_sensor_types'),
    path('sensors/', post_sensor, name='post_sensor'),
    path('sensors/<str:sensor_id>', get_sensor, name='get_sensor'),
    path('sensors/<str:sensor_id>', put_sensor, name='update_sensor'),
    path('fpf-ids/', post_fpf_id, name='post_fpf_id'),
    path('api-keys/', post_api_key, name='post_api_key'),
]
