from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from fpf_sensor_service.services import create_sensor_config, update_sensor_config, get_sensor_config
from fpf_sensor_service.sensors import typed_sensor_factory


@api_view(['POST'])
def post_sensor(request):
    serializer = create_sensor_config(request.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def update_sensor(request, sensor_id):
    serializer = update_sensor_config(request.data, sensor_id)
    return Response(serializer.data)


@api_view(['GET'])
def get_sensor(request, sensor_id):
    serializer = get_sensor_config(sensor_id)
    return Response(serializer.data)


@api_view(['GET'])
def get_available_sensor_types(request):
    return Response(typed_sensor_factory.get_available_sensor_types())

