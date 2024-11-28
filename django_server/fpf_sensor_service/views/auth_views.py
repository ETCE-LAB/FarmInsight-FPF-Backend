from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from fpf_sensor_service.models import Configuration, ConfigurationKeys


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_fpf_id(request):
    Configuration.objects.create(
        key=ConfigurationKeys.FPF_ID.value,
        value=request.data[ConfigurationKeys.FPF_ID.value],
    )
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_api_key(request):
    configuration = Configuration.objects.filter(key=ConfigurationKeys.FPF_ID.value).first()
    if configuration is None:
        Configuration.objects.create(
            key=ConfigurationKeys.API_KEY.value,
            value=request.data[ConfigurationKeys.API_KEY.value],
        )
    else:
        configuration.value = request.data[ConfigurationKeys.API_KEY.value]
        configuration.save()

    return Response(status=status.HTTP_200_OK)