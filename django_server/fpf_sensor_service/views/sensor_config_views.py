from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from fpf_sensor_service.services.sensor_config_services import update_sensor_interval
from fpf_sensor_service.sensors import TypedSensorFactory


typed_sensor_factory = TypedSensorFactory()


@api_view(['POST'])
def post_sensor_interval(request, sensorId):
    """
    Update the sensor intervall on sqlite db and update the scheduling job intervall.
    :param request: HTTP request
    :param sensorId: GUID of sensor which must already exist in the database
    :return: HTTP response
    """
    data = JSONParser().parse(request)
    response = update_sensor_interval(data, sensorId)
    return JsonResponse(response['data'], status=response['status'])


@api_view(['GET'])
def get_available_sensor_types(request):
    return Response(typed_sensor_factory.get_available_sensor_types())
