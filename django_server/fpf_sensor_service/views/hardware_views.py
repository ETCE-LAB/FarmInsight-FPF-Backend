from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from fpf_sensor_service.utils import get_logger
from fpf_sensor_service.services import set_hardware_order, update_hardware, remove_hardware, create_hardware, get_hardware


logger = get_logger()


class HardwareView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = get_hardware()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = create_hardware(request.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, hardware_id):
        hardware = update_hardware(hardware_id, request.data)
        return Response(hardware.data, status=status.HTTP_200_OK)

    def delete(self, request, hardware_id):
        remove_hardware(hardware_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_hardware_order(request):
    serializer = set_hardware_order(request.data)
    return Response(data=serializer.data, status=status.HTTP_200_OK)