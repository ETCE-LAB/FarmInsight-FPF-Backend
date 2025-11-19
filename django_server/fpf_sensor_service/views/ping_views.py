import requests
from json import JSONDecodeError

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK

from fpf_sensor_service.services import get_sensor_config


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sensor_ping(request, sensor_id):
    sensor = get_sensor_config(sensor_id)
    if not ('additionalInformation' in sensor and 'http' in sensor['additionalInformation']):
        return Response(data={'error': 'Sensors hardware configuration malformed, no ping possible.'}, status=HTTP_404_NOT_FOUND)

    url = sensor['additionalInformation']['http']

    response_raw = ''
    try:
        response_raw = requests.get(url, timeout=10)
        response = response_raw.json()
    except JSONDecodeError:
        response = {'return': response_raw.text}
    except Exception as e:
        return Response(data={'error': f'{e}'}, status=HTTP_200_OK)

    return Response(data=response, status=HTTP_200_OK)
