from django.http import JsonResponse
from .models import SensorConfig
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.parsers import JSONParser
from fpf_sensor_service.scheduler import scheduler
from fpf_sensor_service.logging_utils import get_logger
from fpf_sensor_service.serializers import SensorConfigSerializer
logger = get_logger()


@csrf_exempt
def update_sensor_interval(request, sensorId):
    """
    Update the sensor intervall on sqlite db and update the scheduling job intervall.
    :param request: HTTP request
    :param sensorId: GUID of sensor which must already exist in the database
    :return: HTTP response
    """
    if request.method == 'POST':
        try:
            sensor = SensorConfig.objects.get(id=sensorId)
        except ObjectDoesNotExist:
            return JsonResponse({'error': f'Sensor with sensorId {sensorId} not found.'}, status=404)

        data = JSONParser().parse(request)
        serializer = SensorConfigSerializer(sensor, data=data, partial=True)

        # Validate and update if valid
        if serializer.is_valid():
            serializer.save()

            # Update the job in APScheduler
            job_id = f"sensor_{sensorId}"
            job = scheduler.get_job(job_id)
            if job:
                scheduler.reschedule_job(job_id, trigger='interval', seconds=sensor.intervalSeconds)
                logger.info(f"Updated interval for sensor {sensorId} to {sensor.intervalSeconds} seconds")
                return JsonResponse({'status': 'success', 'sensorId': sensorId, 'newInterval': sensor.intervalSeconds})
            else:
                logger.error(f"No job found for sensor {sensorId}")
                return JsonResponse({'error': f'No scheduled job found for sensor {sensorId}'}, status=404)
        else:
            # Return serializer errors if validation fails
            return JsonResponse(serializer.errors, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
