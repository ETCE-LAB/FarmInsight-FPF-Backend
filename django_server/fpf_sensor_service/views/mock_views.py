import base64
from io import BytesIO
from PIL import Image

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django_server import settings
from fpf_sensor_service.utils import get_logger


logger = get_logger()


@api_view(['GET'])
def get_mock_sensor_value(request, sensor_id):
    logger.debug('requesting mock value', extra={'sensor_id': sensor_id})
    data = {
        'value': 420.69
    }
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_mock_image(request, camera_id):
    # CURRENTLY BROKEN, could not reproduce the cameras returns correctly
    logger.debug('requesting mock image', extra={'camera_id': camera_id})
    with Image.open(settings.DEFAULT_IMAGE_PATH) as file:
        stream = BytesIO()
        file.save(stream, "JPEG")
        return Response(data=base64.b64encode(stream.getvalue()).decode('ascii'), content_type="image/jpg", status=status.HTTP_200_OK)