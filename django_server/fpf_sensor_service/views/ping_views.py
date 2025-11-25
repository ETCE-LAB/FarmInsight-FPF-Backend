import requests

from json import JSONDecodeError

from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from fpf_sensor_service.services import ping_resource, get_sensor_config


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ping(request, resource_id):
    '''
    This returns true/false if the selected resource (sensor with http or hardware) is reachable.
    '''
    try:
        response = ping_resource(resource_id)
    except NotFound:
        return Response(status=HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(data={'error': f'{e}'}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(data={'result': response}, status=HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_value_ping(request, sensor_id):
    '''
    This simply directly sends a http request to the sensor if it has a http field in additionalInformation.
    And returns the response text, used by the admin dashboard to get live access to the sensors.
    '''
    sensor = get_sensor_config(sensor_id).data
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