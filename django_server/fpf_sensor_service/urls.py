from django.urls import path
from fpf_sensor_service.views import post_sensor, get_available_sensor_types, SensorView, post_fpf_id, \
    post_api_key, ActionView, execute_action, get_available_action_script_types, post_action_order, ActionTriggerView, \
    get_action_queue, HardwareView, post_hardware_order


urlpatterns = [
    path('fpf-ids', post_fpf_id, name='post_fpf_id'),
    path('api-keys', post_api_key, name='post_api_key'),

    path('sensors/types', get_available_sensor_types, name='get_available_sensor_types'),
    path('sensors', post_sensor, name='post_sensor'),
    path('sensors/<str:sensor_id>', SensorView.as_view(), name='sensor_views'),

    path('actions', ActionView.as_view(), name='post_action'),
    path('actions/sort-order', post_action_order, name='post_action_order'),
    path('actions/<str:action_id>', ActionView.as_view(), name='action_operations'),
    path('execute-actions/<str:action_id>/<str:trigger_id>', execute_action, name='execute_action'),
    path('action-scripts/types', get_available_action_script_types, name='get_available_action_script_types'),

    path('action-triggers', ActionTriggerView.as_view(),name='post_action_trigger'),
    path('action-triggers/<str:action_trigger_id>', ActionTriggerView.as_view(), name='action_trigger_operations'),

    path('action-queues', get_action_queue, name='get_action_queue'),

    path('hardwares', HardwareView.as_view(), name='get_post_hardware'),
    path('hardwares/sort-order', post_hardware_order, name='post_hardware_order'),
    path('hardwares/<str:hardware_id>', HardwareView.as_view(), name='hardware_edits'),
]
