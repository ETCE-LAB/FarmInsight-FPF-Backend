from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from fpf_sensor_service.serializers import SensorDescriptionSerializer
from fpf_sensor_service.services import create_sensor_config, update_sensor_config, get_sensor_config
from fpf_sensor_service.sensors import TypedSensorFactory


typed_sensor_factory = TypedSensorFactory()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_sensor(request):
    serializer = create_sensor_config(request.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class SensorView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, sensor_id):
        serializer = get_sensor_config(sensor_id)
        return Response(serializer.data)

    def put(self, request, sensor_id):
        serializer = update_sensor_config(request.data, sensor_id)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_sensor_types(request):
    sensor_types = typed_sensor_factory.get_available_sensor_types()
    serializer = SensorDescriptionSerializer(sensor_types, many=True)
    return Response(serializer.data)
