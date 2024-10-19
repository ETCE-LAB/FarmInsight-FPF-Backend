from django.http import JsonResponse
from .models import SensorConfig
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
import json
import logging
from fpf_sensor_service.scheduler import scheduler


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
            sensor = SensorConfig.objects.get(sensorId=sensorId)
        except ObjectDoesNotExist:
            return JsonResponse({'error': f'Sensor with sensorId {sensorId} not found.'}, status=404)

        try:
            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)
            interval_seconds = body_data.get('intervalSeconds')
        except (ValueError, KeyError):
            return JsonResponse({'error': 'Invalid JSON or missing "intervalSeconds"'}, status=400)

        if interval_seconds:
            sensor.intervallSeconds = int(interval_seconds)
            sensor.save()

            # Update the existing job's interval in APScheduler
            job_id = f"sensor_{sensorId}"

            # Modify the existing job if it exists, otherwise log an error
            job = scheduler.get_job(job_id)
            if job:
                scheduler.reschedule_job(job_id, trigger='interval', seconds=sensor.intervallSeconds)
                logging.info(f"Updated interval for sensor {sensorId} to {sensor.intervallSeconds} seconds")
                return JsonResponse({'status': 'success', 'sensorId': sensorId, 'newInterval': sensor.intervallSeconds})
            else:
                logging.error(f"No job found for sensor {sensorId}")
                return JsonResponse({'error': f'No scheduled job found for sensor {sensorId}'}, status=404)

        return JsonResponse({'error': 'intervalSeconds not provided'}, status=400)
